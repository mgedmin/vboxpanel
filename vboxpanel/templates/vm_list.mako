<!DOCTYPE html>
<html>
<head>
  <title>Virtual machines of ${username}@${hostname}</title>
  <link rel="stylesheet" href="${request.application_url}/static/style.css" type="text/css" />
</head>
<body>

  <h1>Virtual machines of ${username}@${hostname}</h1>

  <ul>
% for vm in vms:
    <li>
      ${vm.name}
      <span class="status-${'running' if vm.running else 'not-running'}">
        (${'running' if vm.running else 'not running'})
      </span>
%     if vm.vnc_screen:
      - VNC screen ${vm.vnc_screen}
%         if vm.running:
      <br><img src="${request.route_url('screenshot', name=vm.name)}">
%         endif
%     endif
      <br>
      <form action="" method="POST">
        <input type="hidden" name="name" value="${vm.name}">
%     if vm.running:
        <input type="submit" name="SUSPEND" value="Suspend">
        <input type="submit" name="POWEROFF" value="Power Off">
%     else:
        <input type="submit" name="START" value="Start">
%     endif
      </form>
    </li>
% endfor
  </ul>

</body>
</html>
