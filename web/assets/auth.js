(function () {
  var loginForm = document.getElementById("login-form");
  var accountForm = document.getElementById("account-form");

  function show(text) {
    var el = document.getElementById("auth-msg");
    if (el) el.textContent = text || "";
  }

  function nextPath() {
    var next = new URLSearchParams(location.search).get("next") || "/account/";
    if (!next || next.charAt(0) !== "/" || next.indexOf("//") === 0) return "/account/";
    return next;
  }

  if (loginForm) {
    loginForm.addEventListener("submit", function (event) {
      event.preventDefault();
      show("");
      fetch("/api/login", {
        method: "POST",
        headers: { "content-type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({
          login: loginForm.login.value.trim(),
          password: loginForm.password.value
        })
      }).then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) throw new Error((data && data.error) || "로그인에 실패했습니다.");
          location.href = nextPath();
        });
      }).catch(function (error) {
        show(error.message || "로그인에 실패했습니다.");
      });
    });
  }

  if (!accountForm) return;

  fetch("/api/account", { credentials: "same-origin" }).then(function (response) {
    if (response.status === 401) {
      location.href = "/login/?next=/account/";
      return null;
    }
    return response.json();
  }).then(function (account) {
    if (!account) return;
    accountForm.login.value = account.login || "";
    accountForm.email.value = account.email || "";
  }).catch(function () {
    show("계정 정보를 불러오지 못했습니다.");
  });

  accountForm.addEventListener("submit", function (event) {
    event.preventDefault();
    show("");
    var nextPassword = accountForm.newPassword.value;
    if (nextPassword && nextPassword !== accountForm.confirmPassword.value) {
      show("새 비밀번호가 서로 다릅니다.");
      return;
    }
    fetch("/api/account", {
      method: "POST",
      headers: { "content-type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({
        login: accountForm.login.value.trim(),
        email: accountForm.email.value.trim(),
        currentPassword: accountForm.currentPassword.value,
        newPassword: nextPassword
      })
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) throw new Error((data && data.error) || "저장에 실패했습니다.");
        accountForm.currentPassword.value = "";
        accountForm.newPassword.value = "";
        accountForm.confirmPassword.value = "";
        show("계정 정보를 저장했습니다.");
      });
    }).catch(function (error) {
      show(error.message || "저장에 실패했습니다.");
    });
  });

  var logout = document.getElementById("logout");
  if (logout) {
    logout.addEventListener("click", function () {
      fetch("/api/logout", { method: "POST", credentials: "same-origin" }).finally(function () {
        location.href = "/login/";
      });
    });
  }
})();
