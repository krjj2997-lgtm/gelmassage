(function () {
  var menuLogin = document.getElementById("menu-login");
  if (menuLogin) {
    fetch("/api/account", { credentials: "same-origin" }).then(function (response) {
      if (!response.ok) return null;
      return response.json();
    }).then(function (account) {
      if (!account || !account.login) return;
      menuLogin.textContent = "계정";
      menuLogin.setAttribute("href", "/account/");
    }).catch(function () {});
  }

  var input = document.getElementById("q");
  var regionSel = document.getElementById("sel-region");
  var subSel = document.getElementById("sel-sub");
  var spotSel = document.getElementById("sel-spot");
  var list = document.querySelector(".massage-list");
  var cards = list ? list.querySelectorAll(".massage-card") : [];
  var empty = document.getElementById("empty");
  var note = document.getElementById("result-note");
  var noteBase = note ? note.textContent : "";
  var page = document.body.getAttribute("data-page") || "";
  var pageRegion = document.body.getAttribute("data-region") || "";
  var themeLabels = {
    shop: "마사지",
    outcall: "출장마사지",
    "스웨디시": "스웨디시",
    "타이": "타이마사지",
    "아로마": "아로마마사지",
    "왁싱": "왁싱",
    "중국": "중국마사지",
    "발마사지": "발마사지"
  };
  var tree = {};
  var places = {};
  var currentKind = "";
  var currentTheme = "";

  function fold(value) {
    return (value || "").toLowerCase().replace(/\s+/g, "");
  }

  function fillSelect(select, placeholder, values, selected) {
    if (!select) return;
    var html = '<option value="">' + placeholder + "</option>";
    for (var i = 0; i < values.length; i++) {
      var value = values[i];
      html += '<option value="' + value.replace(/"/g, "&quot;") + '">' + value.replace(/</g, "&lt;") + "</option>";
    }
    select.innerHTML = html;
    select.value = selected && values.indexOf(selected) !== -1 ? selected : "";
    select.disabled = !values.length;
  }

  function subsFor(region) {
    if (!region || !tree[region]) return [];
    return Object.keys(tree[region]);
  }

  function spotsFor(region, sub) {
    if (!region || !sub || !tree[region] || !tree[region][sub]) return [];
    return tree[region][sub].slice().sort(function (a, b) {
      var stationA = a.charAt(a.length - 1) === "역" ? 1 : 0;
      var stationB = b.charAt(b.length - 1) === "역" ? 1 : 0;
      if (stationA !== stationB) return stationA - stationB;
      return a.localeCompare(b, "ko");
    });
  }

  function point(name) {
    var row = places[name];
    if (!row) return null;
    return { lat: row[0], lng: row[1] };
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
    if (km < 1) return Math.max(1, Math.round(km * 1000)) + "m";
    return km.toFixed(1) + "km";
  }

  function shopPoint(card) {
    var lat = Number(card.getAttribute("data-lat"));
    var lng = Number(card.getAttribute("data-lng"));
    if (lat && lng) return { lat: lat, lng: lng };
    return point(card.getAttribute("data-sub") || "");
  }

  function originPoint(sub, spot) {
    var olat = Number(document.body.getAttribute("data-olat"));
    var olng = Number(document.body.getAttribute("data-olng"));
    var embeddedSub = document.body.getAttribute("data-sub") || "";
    var embeddedSpot = document.body.getAttribute("data-spot") || "";
    if (olat && olng && (sub || "") === embeddedSub && (spot || "") === embeddedSpot && (spot || sub)) {
      return { lat: olat, lng: olng };
    }
    if (spot && point(spot)) return point(spot);
    if (sub && point(sub)) return point(sub);
    return null;
  }

  function tierOf(card, sub, spot) {
    var subName = card.getAttribute("data-sub") || "";
    var spots = (card.getAttribute("data-spots") || "").split("|");
    if (!sub) return 0;
    if (subName === sub && spot && spots.indexOf(spot) !== -1) return 0;
    if (subName === sub) return spot ? 1 : 0;
    return 2;
  }

  function rank(card, sub, spot, origin) {
    var here = shopPoint(card);
    if (!sub) {
      card._km = null;
      return here ? -here.lat : 0;
    }
    var distance = origin && here ? kmBetween(origin, here) : 9999;
    card._km = distance;
    return tierOf(card, sub, spot) * 10000 + distance;
  }

  function nameOf(card) {
    var node = card.querySelector(".shop-name");
    return node ? node.textContent : "";
  }

  function esc(value) {
    return String(value || "").replace(/[&<>"']/g, function (ch) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch];
    });
  }

  function setMeta(selector, attr, value) {
    var node = document.querySelector(selector);
    if (node && value) node.setAttribute(attr, value);
  }

  function landingPhrase(sub, spot) {
    var topic = themeLabels[currentTheme] || (currentKind === "outcall" ? "출장마사지" : "마사지");
    var embeddedSub = document.body.getAttribute("data-sub") || "";
    var embeddedSpot = document.body.getAttribute("data-spot") || "";
    var embeddedPlace = document.body.getAttribute("data-place") || "";
    var place = "";
    if (embeddedPlace && (sub || "") === embeddedSub && (spot || "") === embeddedSpot && (sub || spot)) place = embeddedPlace;
    else place = spot || sub || "";
    if (place) return place + topic + " 20대,30대 사이트 1위";
    if (currentKind || currentTheme) return (page === "region" ? pageRegion : "") + topic + " 20대,30대 사이트 1위";
    return "";
  }

  function paintLanding(sub, spot, count) {
    if (page !== "region" && page !== "all") return;
    var filtered = !!(sub || spot || currentKind || currentTheme);
    var heading = landingPhrase(sub, spot);
    var baseTitle = document.body.getAttribute("data-title") || document.title;
    var baseHeading = baseTitle.replace(/ \| 마사지성지$/, "");
    if (!filtered && page === "all") heading = "";
    var title = heading ? heading + " | 마사지성지" : baseTitle;
    var description = heading ? heading + "의 위치, 가격, 영업시간을 비교하세요." : (document.body.getAttribute("data-description") || "");
    var embeddedSub = document.body.getAttribute("data-sub") || "";
    var query = new URLSearchParams();
    if (sub && sub !== embeddedSub) query.set("sub", sub);
    if (spot) query.set("spot", spot);
    if (currentKind === "shop" || currentKind === "outcall") query.set("kind", currentKind);
    if (themeLabels[currentTheme]) query.set("theme", currentTheme);
    var search = query.toString();
    var canon = heading
      ? "https://outcallmassage.co.kr" + location.pathname + (search ? "?" + search : "")
      : (document.body.getAttribute("data-canonical") || "");
    document.title = title;
    var h1 = document.querySelector("#main h1");
    if (h1) h1.textContent = heading || baseHeading;
    setMeta('meta[name="description"]', "content", description);
    setMeta('link[rel="canonical"]', "href", canon);
    setMeta('meta[property="og:title"]', "content", title);
    setMeta('meta[property="og:description"]', "content", description);
    setMeta('meta[property="og:url"]', "content", canon);
    setMeta('meta[name="twitter:title"]', "content", title);
    setMeta('meta[name="twitter:description"]', "content", description);
    var robots = document.querySelector('meta[name="robots"]');
    if (robots) robots.setAttribute("content", filtered && count === 0 ? "noindex,follow" : "index,follow");
    var crumb = document.getElementById("crumb-current");
    if (crumb && heading) crumb.textContent = heading;
    var ld = document.getElementById("listing-ld");
    var nav = document.querySelector(".crumb");
    if (ld && nav) {
      var names = [];
      nav.querySelectorAll("a, span").forEach(function (node) { names.push(node.textContent); });
      var items = names.map(function (name, index) {
        return { "@type": "ListItem", position: index + 1, name: name };
      });
      if (items[0]) items[0].item = "https://outcallmassage.co.kr/";
      if (canon && items.length > 1) items[items.length - 1].item = canon;
      ld.textContent = JSON.stringify({ "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: items });
    }
    if (note) {
      if (!filtered) note.textContent = noteBase;
      else if (count === 0) note.textContent = heading + "에 해당하는 업체가 없습니다.";
      else if (spot) note.textContent = spot + "에서 가까운 " + (document.body.getAttribute("data-sub") || "") + " 업체 " + count + "곳입니다.";
      else note.textContent = heading + " " + count + "곳입니다.";
    }
  }

  function reloadCards() {
    cards = list ? list.querySelectorAll(".massage-card") : [];
  }

  function apply(push) {
    if (!regionSel) return;
    reloadCards();
    var region = regionSel.value;
    var sub = subSel ? subSel.value : "";
    var spot = spotSel ? spotSel.value : "";
    var query = fold(input ? input.value : "");
    var shown = [];
    for (var i = 0; i < cards.length; i++) {
      var card = cards[i];
      var ok = true;
      if (region && card.getAttribute("data-region") !== region) ok = false;
      if (ok && currentKind && card.getAttribute("data-kind") !== currentKind) ok = false;
      if (ok && currentTheme && fold(card.getAttribute("data-q")).indexOf(fold(currentTheme)) === -1) ok = false;
      if (ok && query && fold(card.getAttribute("data-q")).indexOf(query) === -1) ok = false;
      card.hidden = !ok;
      if (ok) shown.push(card);
    }
    var origin = originPoint(sub, spot);
    shown.sort(function (a, b) {
      var diff = rank(a, sub, spot, origin) - rank(b, sub, spot, origin);
      if (diff) return diff;
      return nameOf(a).localeCompare(nameOf(b), "ko");
    });
    if (list) {
      for (var n = 0; n < shown.length; n++) list.appendChild(shown[n]);
    }
    for (var k = 0; k < cards.length; k++) {
      var kmNode = cards[k].querySelector(".shop-km");
      if (!kmNode) continue;
      kmNode.textContent = origin && !cards[k].hidden && isFinite(cards[k]._km) ? fmtKm(cards[k]._km) : "";
    }
    if (empty) empty.hidden = shown.length !== 0;
    paintLanding(sub, spot, shown.length);
    if (push && (page === "region" || page === "all")) {
      var embeddedSub = document.body.getAttribute("data-sub") || "";
      var embeddedSpot = document.body.getAttribute("data-spot") || "";
      var params = new URLSearchParams();
      if (sub && sub !== embeddedSub) params.set("sub", sub);
      if (spot && spot !== embeddedSpot) params.set("spot", spot);
      if (currentKind) params.set("kind", currentKind);
      if (currentTheme) params.set("theme", currentTheme);
      if (input && input.value.trim()) params.set("q", input.value.trim());
      var next = params.toString();
      history.replaceState(null, "", location.pathname + (next ? "?" + next : ""));
    }
  }

  function markChips() {
    var all = document.getElementById("chip-all");
    var shop = document.getElementById("chip-shop");
    var outcall = document.getElementById("chip-outcall");
    var themeBtn = document.getElementById("chip-theme");
    var themeLabel = document.getElementById("theme-label");
    var themeSel = document.getElementById("sel-theme");
    if (all) all.classList.toggle("active", !currentKind && !currentTheme);
    if (shop) shop.classList.toggle("active", currentKind === "shop" && !currentTheme);
    if (outcall) outcall.classList.toggle("active", currentKind === "outcall" && !currentTheme);
    if (themeBtn) themeBtn.classList.toggle("active", !!currentTheme);
    if (themeLabel) {
      var picked = currentTheme ? document.querySelector('.type-dropdown-item[data-theme="' + currentTheme + '"]') : null;
      themeLabel.textContent = picked ? picked.textContent : "테마보기";
    }
    if (themeSel) {
      themeSel.value = currentTheme;
      themeSel.classList.toggle("is-on", !!currentTheme);
    }
  }

  function setFilter(kind, theme) {
    currentKind = kind || "";
    currentTheme = theme || "";
    markChips();
    apply(true);
  }

  function regionSlug() {
    var option = regionSel.options[regionSel.selectedIndex];
    return option ? option.getAttribute("data-slug") || "" : "";
  }

  function goRegion() {
    var region = regionSel.value;
    if (!region) {
      var reset = new URLSearchParams();
      if (currentKind) reset.set("kind", currentKind);
      if (currentTheme) reset.set("theme", currentTheme);
      if (input && input.value.trim()) reset.set("q", input.value.trim());
      var resetTail = reset.toString();
      location.href = "/all/" + (resetTail ? "?" + resetTail : "");
      return;
    }
    var extra = new URLSearchParams();
    if (currentKind) extra.set("kind", currentKind);
    if (currentTheme) extra.set("theme", currentTheme);
    if (input && input.value.trim()) extra.set("q", input.value.trim());
    var tail = extra.toString();
    if (page === "region" && region === pageRegion) {
      if (document.body.getAttribute("data-sub")) {
        location.href = "/region/" + regionSlug() + "/" + (tail ? "?" + tail : "");
        return;
      }
      fillSelect(subSel, "세부지역", subsFor(region), "");
      fillSelect(spotSel, "동/역", [], "");
      apply(true);
      return;
    }
    var slug = regionSlug();
    if (!slug) {
      location.href = "/all/" + (tail ? "?" + tail : "");
      return;
    }
    location.href = "/region/" + slug + "/" + (tail ? "?" + tail : "");
  }

  function bind() {
    if (!regionSel) return;
    if (subSel) {
      subSel.addEventListener("change", function () {
        if (page === "region" && regionSlug()) {
          var extra = new URLSearchParams();
          if (currentKind) extra.set("kind", currentKind);
          if (currentTheme) extra.set("theme", currentTheme);
          if (input && input.value.trim()) extra.set("q", input.value.trim());
          var tail = extra.toString();
          var next = subSel.value
            ? "/region/" + regionSlug() + "/" + encodeURIComponent(subSel.value) + "/"
            : "/region/" + regionSlug() + "/";
          location.href = next + (tail ? "?" + tail : "");
          return;
        }
        fillSelect(spotSel, "동/역", spotsFor(regionSel.value, subSel.value), "");
        apply(true);
      });
    }
    if (spotSel) spotSel.addEventListener("change", function () {
      if (page === "region" && regionSlug() && subSel && subSel.value) {
        var extra = new URLSearchParams();
        if (currentKind) extra.set("kind", currentKind);
        if (currentTheme) extra.set("theme", currentTheme);
        if (input && input.value.trim()) extra.set("q", input.value.trim());
        var tail = extra.toString();
        var next = "/region/" + regionSlug() + "/" + encodeURIComponent(subSel.value) + "/";
        if (spotSel.value) next += encodeURIComponent(spotSel.value) + "/";
        location.href = next + (tail ? "?" + tail : "");
        return;
      }
      apply(true);
    });
    if (input && page !== "home") input.addEventListener("input", function () { apply(false); });

    var params = new URLSearchParams(location.search);
    var region = page === "region" ? pageRegion : (params.get("region") || "");
    var pageSub = document.body.getAttribute("data-sub") || "";
    var pageSpot = document.body.getAttribute("data-spot") || "";
    var sub = params.get("sub") || pageSub;
    var spot = params.get("spot") || pageSpot;
    currentKind = params.get("kind") || "";
    currentTheme = params.get("theme") || "";
    if (currentKind !== "shop" && currentKind !== "outcall") currentKind = "";
    if (!themeLabels[currentTheme]) currentTheme = "";
    var themeSel = document.getElementById("sel-theme");
    if (themeSel) themeSel.value = currentTheme;
    if (input && params.get("q")) input.value = params.get("q");
    if (region) regionSel.value = region;
    fillSelect(subSel, "세부지역", subsFor(regionSel.value), sub);
    fillSelect(spotSel, "동/역", spotsFor(regionSel.value, subSel ? subSel.value : ""), spot);
    markChips();
    if (page === "all" && params.get("region") && regionSlug()) {
      var target = "/region/" + regionSlug() + "/";
      var extra = new URLSearchParams();
      if (sub) extra.set("sub", sub);
      if (spot) extra.set("spot", spot);
      if (currentKind) extra.set("kind", currentKind);
      if (currentTheme) extra.set("theme", currentTheme);
      if (params.get("q")) extra.set("q", params.get("q"));
      var tail = extra.toString();
      location.replace(target + (tail ? "?" + tail : ""));
      return;
    }
    if (page === "region" || page === "all") apply(false);
  }

  var inquiry = document.getElementById("inquiry-form");
  if (inquiry) inquiry.addEventListener("submit", function (event) {
    event.preventDefault();
    var shopName = (document.getElementById("shop-name").value || "").trim();
    var region = (document.getElementById("shop-region").value || "").trim();
    var phone = (document.getElementById("shop-phone").value || "").trim();
    var note = (document.getElementById("shop-note").value || "").trim();
    var body = "업체명: " + shopName + "\n지역: " + region + "\n연락처: " + phone + "\n내용: " + note;
    var msg = document.getElementById("auth-msg");
    if (msg) msg.textContent = "메일 앱이 열립니다.";
    location.href = "mailto:krjj2997@gmail.com?subject=" + encodeURIComponent("마사지성지 입점 문의") + "&body=" + encodeURIComponent(body);
  });

  var menu = document.getElementById("side-menu");
  var backdrop = document.getElementById("nav-backdrop");
  var menuBtn = document.getElementById("open-menu");
  function setMenu(open) {
    if (!menu) return;
    menu.hidden = !open;
    if (backdrop) backdrop.hidden = !open;
    if (menuBtn) menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
  }
  if (menuBtn) menuBtn.addEventListener("click", function () { setMenu(menu.hidden); });
  if (backdrop) backdrop.addEventListener("click", function () { setMenu(false); });
  var openSearch = document.getElementById("open-search");
  if (openSearch) openSearch.addEventListener("click", function () {
    var box = document.getElementById("q");
    if (!box) {
      location.href = "/all/#q";
      return;
    }
    box.scrollIntoView({ block: "center" });
    box.focus();
  });
  if (input && location.hash === "#q") {
    input.scrollIntoView({ block: "center" });
    input.focus();
  }
  var openRegion = document.getElementById("open-region");
  if (openRegion && openRegion.tagName !== "A") openRegion.addEventListener("click", function () {
    if (!regionSel) { location.href = "/all/"; return; }
    regionSel.scrollIntoView({ block: "center" });
    regionSel.focus();
  });
  var themeSel = document.getElementById("sel-theme");
  if (themeSel) {
    themeSel.addEventListener("change", function () {
      if (page === "home") {
        var next = new URLSearchParams();
        if (themeSel.value) next.set("theme", themeSel.value);
        var query = next.toString();
        location.href = "/all/" + (query ? "?" + query : "");
        return;
      }
      setFilter(currentKind, themeSel.value);
    });
  }
  ["chip-all", "chip-shop", "chip-outcall"].forEach(function (id) {
    var button = document.getElementById(id);
    if (!button) return;
    button.addEventListener("click", function () {
      setFilter(button.getAttribute("data-kind") || "", "");
    });
  });
  var infoBtn = document.getElementById("related-info");
  var infoDialog = document.getElementById("info-dialog");
  if (infoBtn && infoDialog) infoBtn.addEventListener("click", function () { infoDialog.showModal(); });
  var routeBtn = document.getElementById("open-route");
  var routeDialog = document.getElementById("route-dialog");
  if (routeBtn && routeDialog) {
    routeBtn.addEventListener("click", function () { routeDialog.showModal(); });
    var sheet = routeDialog.querySelector(".route-sheet");
    if (sheet) sheet.addEventListener("click", function (event) { event.stopPropagation(); });
    routeDialog.addEventListener("click", function () { routeDialog.close(); });
    var closeRoute = document.getElementById("close-route");
    if (closeRoute) closeRoute.addEventListener("click", function () { routeDialog.close(); });
  }

  if (!regionSel && !input) return;
  if (regionSel) regionSel.addEventListener("change", goRegion);
  var listFrom = document.body.getAttribute("data-list") || "";
  var listReady = Promise.resolve();
  if (list && listFrom && !list.querySelector(".massage-card")) {
    listReady = fetch(listFrom).then(function (response) { return response.text(); }).then(function (html) {
      var parsed = new DOMParser().parseFromString(html, "text/html");
      var remote = parsed.querySelector(".massage-list");
      if (remote) list.innerHTML = remote.innerHTML;
    }).catch(function () {});
  }
  Promise.all([
    fetch("/assets/locations.json?v=2").then(function (response) { return response.json(); }),
    fetch("/assets/places.json?v=2").then(function (response) { return response.json(); }),
    listReady
  ]).then(function (rows) {
    tree = rows[0] || {};
    places = rows[1] || {};
    bind();
  }).catch(function () { bind(); });
})();
