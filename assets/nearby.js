(function () {
  var KAKAO_JS_KEY = "d3b29db8ca0f290af256da095202aa77";
  var mapEl = document.getElementById("nearby-map");
  var listEl = document.getElementById("nearby-list");
  var statusEl = document.getElementById("nearby-status");
  var wrap = document.querySelector(".nearby-wrap");
  if (!mapEl || !listEl || !statusEl) return;

  var shops = [];
  var origin = { lat: 37.5546, lng: 126.9706 };
  var radius = 0;
  var cat = "";
  var theme = "";
  var healing = false;
  var located = false;
  var selectedId = "";
  var usingKakao = false;
  var kakaoMap = null;
  var kakaoPins = [];
  var leafletMap = null;
  var leafletPins = [];
  var leafletMe = null;
  var leafletCircle = null;
  var picker = document.getElementById("nearby-picker");
  var pickerList = document.getElementById("nearby-picker-list");
  var suppressMapEvent = false;

  function esc(value) {
    return String(value || "").replace(/[&<>"']/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }

  function kmBetween(a, b) {
    var earth = 6371;
    var dLat = ((b.lat - a.lat) * Math.PI) / 180;
    var dLng = ((b.lng - a.lng) * Math.PI) / 180;
    var lat1 = (a.lat * Math.PI) / 180;
    var lat2 = (b.lat * Math.PI) / 180;
    var h = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
    return 2 * earth * Math.asin(Math.min(1, Math.sqrt(h)));
  }

  function fmtKm(km) {
    if (km < 1) return Math.round(km * 1000) + "m";
    return km.toFixed(1) + "km";
  }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var script = document.createElement("script");
      script.src = src;
      script.async = true;
      script.onload = function () { resolve(); };
      script.onerror = function () { reject(new Error(src)); };
      document.head.appendChild(script);
    });
  }

  function loadCss(href) {
    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = href;
    document.head.appendChild(link);
  }

  function rowsInRange() {
    var rows = [];
    for (var i = 0; i < shops.length; i++) {
      var shop = shops[i];
      if (cat === "shop" && shop.kind !== "shop") continue;
      if (cat === "outcall" && shop.kind !== "outcall") continue;
      if (cat === "one" && !shop.one) continue;
      if (theme && String(shop.q || "").indexOf(theme) === -1) continue;
      if (healing && shop.kind !== "shop") continue;
      shop.km = kmBetween(origin, shop);
      if (radius && shop.km > radius) continue;
      if (!radius && !shopInView(shop)) continue;
      rows.push(shop);
    }
    rows.sort(function (a, b) { return a.km - b.km; });
    return rows;
  }

  function groupOverlapping(rows) {
    var used = [];
    var groups = [];
    for (var i = 0; i < rows.length; i++) {
      if (used[i]) continue;
      var group = [rows[i]];
      used[i] = true;
      for (var j = i + 1; j < rows.length; j++) {
        if (used[j]) continue;
        if (kmBetween(rows[i], rows[j]) * 1000 <= 45) {
          group.push(rows[j]);
          used[j] = true;
        }
      }
      groups.push(group);
    }
    return groups;
  }

  function pinHtml(group) {
    if (group.length > 1) {
      return '<div class="map-pin map-pin--cluster"><button type="button" class="map-cluster">+' + group.length + "</button></div>";
    }
    var shop = group[0];
    var on = String(shop.id) === String(selectedId) ? " is-selected" : "";
    return '<div class="map-pin"><button type="button" class="map-label' + on + '"><span class="map-name">' +
      esc(shop.name) + '</span><span class="map-price">' + esc(shop.short || shop.price) + "</span></button></div>";
  }

  function closePicker() {
    if (picker) picker.hidden = true;
  }

  function openPicker(group) {
    if (!picker || !pickerList) return;
    pickerList.innerHTML = group.map(function (shop) {
      return '<button type="button" class="pick-row" data-id="' + esc(shop.id) + '"><span class="pick-name">' +
        esc(shop.name) + '</span><span class="pick-price">' + esc(shop.short || shop.price) + "</span></button>";
    }).join("");
    picker.hidden = false;
  }

  function viewBox() {
    if (usingKakao && kakaoMap && kakaoMap.getBounds) {
      var bounds = kakaoMap.getBounds();
      var sw = bounds.getSouthWest();
      var ne = bounds.getNorthEast();
      return { south: sw.getLat(), north: ne.getLat(), west: sw.getLng(), east: ne.getLng() };
    }
    if (leafletMap && leafletMap.getBounds) {
      var box = leafletMap.getBounds();
      return { south: box.getSouth(), north: box.getNorth(), west: box.getWest(), east: box.getEast() };
    }
    return null;
  }

  function shopInView(shop) {
    var box = viewBox();
    if (!box) return false;
    return shop.lat >= box.south && shop.lat <= box.north && shop.lng >= box.west && shop.lng <= box.east;
  }

  function paintList(rows) {
    var where = located ? "내 위치" : "서울역";
    var title = radius ? where + " 기준 가까운 순 " + rows.length + "곳" : "이 화면 안 " + rows.length + "곳";
    statusEl.firstChild.textContent = (radius ? "기준 " + where + " · 가까운 순 " : "이 화면 · ") + rows.length + "곳" + (usingKakao ? "" : " · 이 주소는 카카오맵 도메인이 아니라 기본 지도입니다");
    if (!rows.length) {
      var empty = radius ? "조건에 맞는 업체가 없습니다." : "지도를 넓히면 주변 업체가 보입니다.";
      listEl.innerHTML = "<h2>" + title + '</h2><p class="empty">' + empty + "</p>";
      return;
    }
    var shown = rows.slice();
    if (selectedId) {
      shown.sort(function (a, b) {
        var pickedA = String(a.id) === String(selectedId) ? 0 : 1;
        var pickedB = String(b.id) === String(selectedId) ? 0 : 1;
        if (pickedA !== pickedB) return pickedA - pickedB;
        return a.km - b.km;
      });
    }
    listEl.innerHTML = "<h2>" + esc(title) + "</h2>" + shown.map(function (shop) {
      var selected = String(shop.id) === String(selectedId) ? " is-selected" : "";
      var badge = shop.kind === "outcall" ? "출장마사지" : "힐링샵";
      var badgeClass = shop.kind === "outcall" ? "shop-type shop-type-outcall" : "shop-type";
      var img = shop.img ? '<img src="' + esc(shop.img) + '" alt="' + esc(shop.name) + '" width="92" height="118" loading="lazy">' : "";
      return '<a class="shop-card' + selected + '" id="card-' + esc(shop.id) + '" href="/shop/' + encodeURIComponent(shop.id) + '/">' +
        '<div class="card-image">' + img + '<div class="image-overlay"><div class="' + badgeClass + '">' + badge + "</div></div></div>" +
        '<div class="card-body"><div class="row1"><h3><span class="card-name">' + esc(shop.name) + '</span></h3><span class="km">' +
        fmtKm(shop.km) + "</span></div><p>" + esc(shop.addr || shop.place || "주소 없음") + "</p><p>" +
        esc(shop.hours || "영업시간 정보 없음") + '</p><p class="price"><span class="price-label">최저가</span>' +
        esc(shop.price || "가격 문의") + "</p></div></a>";
    }).join("");
  }

  function clearPins() {
    for (var i = 0; i < kakaoPins.length; i++) kakaoPins[i].setMap(null);
    kakaoPins = [];
    for (var n = 0; n < leafletPins.length; n++) leafletMap.removeLayer(leafletPins[n]);
    leafletPins = [];
  }

  function bindPin(node, group) {
    var button = node.querySelector("button");
    if (!button) return;
    button.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      if (group.length === 1) selectShop(group[0].id);
      else openPicker(group);
    });
  }

  function focusMap() {
    var dLat = radius ? radius / 111 : 0;
    var dLng = radius ? radius / (111 * Math.cos((origin.lat * Math.PI) / 180)) : 0;
    suppressMapEvent = true;
    if (usingKakao && kakaoMap) {
      if (typeof kakaoMap.relayout === "function") kakaoMap.relayout();
      if (!radius) {
        kakaoMap.setLevel(2);
        kakaoMap.setCenter(new kakao.maps.LatLng(origin.lat, origin.lng));
      } else {
        kakaoMap.setBounds(new kakao.maps.LatLngBounds(
          new kakao.maps.LatLng(origin.lat - dLat, origin.lng - dLng),
          new kakao.maps.LatLng(origin.lat + dLat, origin.lng + dLng)
        ));
      }
    } else if (leafletMap) {
      leafletMap.invalidateSize();
      if (!radius) leafletMap.setView([origin.lat, origin.lng], 17);
      else {
        leafletMap.fitBounds([
          [origin.lat - dLat, origin.lng - dLng],
          [origin.lat + dLat, origin.lng + dLng]
        ], { padding: [20, 20] });
      }
    }
    setTimeout(function () { suppressMapEvent = false; }, 600);
  }

  function onMapIdle() {
    if (suppressMapEvent || radius) return;
    render(false);
  }

  function drawPins(rows, fit) {
    closePicker();
    clearPins();
    var shown = rows;
    var groups = groupOverlapping(shown);
    var mePos = null;
    if (usingKakao) {
      mePos = new kakao.maps.LatLng(origin.lat, origin.lng);
      var meNode = document.createElement("div");
      meNode.className = "my-dot";
      var me = new kakao.maps.CustomOverlay({ position: mePos, content: meNode, xAnchor: 0.5, yAnchor: 0.5, zIndex: 4 });
      me.setMap(kakaoMap);
      kakaoPins.push(me);
      if (radius) {
        var circle = new kakao.maps.Circle({
          center: mePos,
          radius: radius * 1000,
          strokeWeight: 2,
          strokeColor: "#667eea",
          strokeOpacity: 0.9,
          fillColor: "#667eea",
          fillOpacity: 0.08
        });
        circle.setMap(kakaoMap);
        kakaoPins.push(circle);
      }
    } else if (leafletMap) {
      if (leafletMe) leafletMap.removeLayer(leafletMe);
      leafletMe = L.marker([origin.lat, origin.lng], {
        icon: L.divIcon({ className: "", html: '<div class="my-dot"></div>', iconSize: [16, 16], iconAnchor: [8, 8] }),
        zIndexOffset: 1000,
        interactive: false
      }).addTo(leafletMap);
      if (leafletCircle) leafletMap.removeLayer(leafletCircle);
      leafletCircle = null;
      if (radius) {
        leafletCircle = L.circle([origin.lat, origin.lng], {
          radius: radius * 1000,
          color: "#667eea",
          fillColor: "#667eea",
          fillOpacity: 0.08,
          weight: 2
        }).addTo(leafletMap);
      }
    }
    var bounds = usingKakao ? new kakao.maps.LatLngBounds() : null;
    if (bounds) bounds.extend(mePos);
    for (var i = 0; i < groups.length; i++) {
      (function (group) {
        var shop = group[0];
        if (usingKakao) {
          var node = document.createElement("div");
          node.innerHTML = pinHtml(group);
          var pin = node.firstChild;
          bindPin(pin, group);
          var pos = new kakao.maps.LatLng(shop.lat, shop.lng);
          var overlay = new kakao.maps.CustomOverlay({ position: pos, content: pin, xAnchor: 0.5, yAnchor: 1, clickable: true, zIndex: 2 });
          overlay.setMap(kakaoMap);
          kakaoPins.push(overlay);
          bounds.extend(pos);
        } else if (leafletMap) {
          var marker = L.marker([shop.lat, shop.lng], {
            icon: L.divIcon({
              className: "map-label-icon",
              html: pinHtml(group),
              iconSize: group.length > 1 ? [52, 56] : [210, 58],
              iconAnchor: group.length > 1 ? [26, 56] : [105, 58]
            })
          });
          marker.on("click", function (event) {
            if (event.originalEvent) L.DomEvent.stopPropagation(event.originalEvent);
            if (group.length === 1) selectShop(group[0].id);
            else openPicker(group);
          });
          marker.addTo(leafletMap);
          leafletPins.push(marker);
        }
      })(groups[i]);
    }
  }

  function render(fit) {
    if (wrap) wrap.classList.remove("is-homecare");
    if (fit) focusMap();
    var rows = rowsInRange();
    paintList(rows);
    drawPins(rows, false);
  }

  function selectShop(id) {
    selectedId = String(id);
    closePicker();
    suppressMapEvent = true;
    var shop = null;
    for (var s = 0; s < shops.length; s++) {
      if (String(shops[s].id) === selectedId) shop = shops[s];
    }
    var rows = rowsInRange();
    if (shop && !rows.some(function (row) { return String(row.id) === selectedId; })) {
      shop.km = kmBetween(origin, shop);
      rows.unshift(shop);
    }
    paintList(rows);
    drawPins(rows, false);
    if (listEl) listEl.scrollTop = 0;
    if (shop && usingKakao && kakaoMap) {
      kakaoMap.setLevel(4);
      kakaoMap.panTo(new kakao.maps.LatLng(shop.lat, shop.lng));
    } else if (shop && leafletMap) {
      leafletMap.setView([shop.lat, shop.lng], 16);
    }
    setTimeout(function () { suppressMapEvent = false; }, 800);
  }

  function mark(bar, attr, value) {
    var buttons = bar.querySelectorAll("button[" + attr + "]");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].classList.toggle("active", buttons[i].getAttribute(attr) === value);
    }
  }

  var catBar = document.getElementById("nearby-cats");
  if (catBar) catBar.addEventListener("click", function (event) {
    var button = event.target.closest("button[data-cat]");
    if (!button) return;
    cat = button.getAttribute("data-cat") || "";
    mark(catBar, "data-cat", cat);
    render();
  });

  var radiusBar = document.getElementById("nearby-radius");
  if (radiusBar) radiusBar.addEventListener("click", function (event) {
    var button = event.target.closest("button[data-km]");
    if (!button || button.disabled) return;
    radius = Number(button.getAttribute("data-km"));
    mark(radiusBar, "data-km", button.getAttribute("data-km"));
    render(true);
  });

  var themeToggle = document.getElementById("nearby-theme-toggle");
  var themeBox = document.getElementById("nearby-themes");
  if (themeToggle && themeBox) themeToggle.addEventListener("click", function () {
    themeBox.hidden = !themeBox.hidden;
    themeToggle.classList.toggle("is-open", !themeBox.hidden);
    themeToggle.classList.toggle("active", !themeBox.hidden || !!theme);
  });
  if (themeBox) themeBox.addEventListener("click", function (event) {
    var button = event.target.closest("button[data-theme]");
    if (!button) return;
    theme = button.getAttribute("data-theme") || "";
    mark(themeBox, "data-theme", theme);
    if (themeToggle) themeToggle.classList.toggle("active", !!theme || !themeBox.hidden);
    render();
  });

  var heal = document.getElementById("nearby-healing");
  if (heal) heal.addEventListener("click", function () {
    healing = !healing;
    heal.classList.toggle("is-on", healing);
    heal.setAttribute("aria-pressed", healing ? "true" : "false");
    render();
  });

  if (pickerList) pickerList.addEventListener("click", function (event) {
    var button = event.target.closest("button[data-id]");
    if (!button) return;
    selectShop(button.getAttribute("data-id"));
  });

  function locate(fresh) {
    if (!navigator.geolocation) {
      statusEl.firstChild.textContent = "이 브라우저에서는 현재 위치를 쓸 수 없어 서울역 기준으로 보여 줍니다.";
      render(true);
      return;
    }
    statusEl.firstChild.textContent = "현재 위치를 찾는 중입니다.";
    navigator.geolocation.getCurrentPosition(function (pos) {
      located = true;
      origin = { lat: pos.coords.latitude, lng: pos.coords.longitude };
      render(true);
    }, function () {
      located = false;
      statusEl.firstChild.textContent = "위치를 허용하지 않아 서울역 기준으로 보여 줍니다.";
      render(true);
    }, { enableHighAccuracy: true, timeout: fresh ? 15000 : 10000, maximumAge: fresh ? 0 : 60000 });
  }

  var gps = document.getElementById("nearby-gps");
  if (gps) gps.addEventListener("click", function () { locate(true); });

  function bootLeaflet() {
    loadCss("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css");
    return loadScript("https://unpkg.com/leaflet@1.9.4/dist/leaflet.js").then(function () {
      leafletMap = L.map(mapEl, { scrollWheelZoom: true }).setView([origin.lat, origin.lng], 17);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 18,
        attribution: "&copy; OpenStreetMap"
      }).addTo(leafletMap);
      leafletMap.on("click", closePicker);
      leafletMap.on("moveend", onMapIdle);
    });
  }

  function bootKakao() {
    var src = "https://dapi.kakao.com/v2/maps/sdk.js?appkey=" + encodeURIComponent(KAKAO_JS_KEY) + "&autoload=false";
    return loadScript(src).then(function () {
      return new Promise(function (resolve, reject) {
        if (!window.kakao || !kakao.maps || !kakao.maps.load) {
          reject(new Error("kakao"));
          return;
        }
        var timer = setTimeout(function () { reject(new Error("kakao timeout")); }, 4000);
        kakao.maps.load(function () {
          clearTimeout(timer);
          try {
            kakaoMap = new kakao.maps.Map(mapEl, {
              center: new kakao.maps.LatLng(origin.lat, origin.lng),
              level: 2
            });
            kakao.maps.event.addListener(kakaoMap, "click", closePicker);
            kakao.maps.event.addListener(kakaoMap, "idle", onMapIdle);
            usingKakao = true;
            resolve();
          } catch (error) {
            reject(error);
          }
        });
      });
    });
  }

  fetch("/assets/nearby.json?v=4")
    .then(function (response) { return response.json(); })
    .then(function (data) {
      shops = data || [];
      return bootKakao().catch(function () { return bootLeaflet(); });
    })
    .then(function () { locate(); })
    .catch(function () {
      statusEl.firstChild.textContent = "지도 정보를 불러오지 못했습니다.";
    });
})();
