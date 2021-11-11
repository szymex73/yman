from dasbus.connection import SessionMessageBus


class YakuakeSession(object):
    def __init__(self, bus: SessionMessageBus, session_id: int) -> None:
        self.bus = bus
        self.id = session_id

        self.tab_proxy = self.bus.get_proxy('org.kde.yakuake', '/yakuake/tabs')
        self.session_proxy = self.bus.get_proxy('org.kde.yakuake', '/yakuake/sessions')

        terminal_ids = self.session_proxy.terminalIdsForSessionId(self.id)
        self.terminal_id = [int(tid) for tid in terminal_ids.split(',')][0]
        self.terminal_proxy = self.bus.get_proxy('org.kde.yakuake', f'/Sessions/{self.terminal_id + 1}')

    def send_text(self, text: str) -> None:
        self.terminal_proxy.sendText(text)

    def run_command(self, command: str) -> None:
        self.terminal_proxy.runCommand(command)

    @property
    def title(self) -> str:
        """Gets or sets the tab title"""
        return self.tab_proxy.tabTitle(self.id)

    @title.setter
    def title(self, title: str) -> str:
        self.tab_proxy.setTabTitle(self.id, title)

    @property
    def pid(self) -> int:
        """Gets the process id"""
        return self.terminal_proxy.processId()

    @property
    def fg_pid(self) -> int:
        """Gets the foreground process id"""
        return self.terminal_proxy.foregroundProcessId()


class Yakuake(object):
    def __init__(self) -> None:
        self.bus = SessionMessageBus()

        self.session_proxy = self.bus.get_proxy('org.kde.yakuake', '/yakuake/sessions')
        self.tabs_proxy = self.bus.get_proxy('org.kde.yakuake', '/yakuake/tabs')

    def get_current_session_id(self) -> int:
        """Returns the currently active session"""
        return self.session_proxy.activeSessionId()

    def get_session_id_at_tab(self, tab_index: int) -> int:
        """Return the session ID of a session at a given tab index"""
        return self.tabs_proxy.sessionAtTab(tab_index)

    def session_id_for_terminal_id(self, terminal_id: int) -> int:
        """Returns a session ID for a given terminal"""
        return self.session_proxy.sessionIdForTerinalId(terminal_id)

    def terminal_id_for_session_id(self, session_id: int) -> int:
        """Returns a list of terminal IDs for a given session"""
        terminal_ids = self.session_proxy.terminalIdsForSessionId(session_id)
        return [int(tid) for tid in terminal_ids.split(',')]

    def get_session_ids(self) -> list[int]:
        """Returns a list of running sessions"""
        session_ids = self.session_proxy.sessionIdList()
        return [int(sid) for sid in session_ids.split(',')]

    def add_session(self) -> int:
        """Spawns a new session with a single terminal"""
        return self.session_proxy.addSession()

    def raise_session(self, session_id: int) -> int:
        """Raises a given session"""
        self.session_proxy.raiseSession(session_id)

    def remove_session(self, session_id: int) -> None:
        """Removes a given session"""
        self.session_proxy.removeSession(session_id)

    def get_tab_session_map(self, skip_current: bool = False) -> dict[int, int]:
        """Returns session IDs mapped to tab indexes"""
        tab_ids = [i for i in range(len(self.get_session_ids()))]
        current_id = self.get_current_session_id()
        if skip_current:
            return dict([(tab_id, self.get_session_id_at_tab(tab_id)) for tab_id in tab_ids if
                         self.get_session_id_at_tab(tab_id) != current_id])
        else:
            return dict([(tab_id, self.get_session_id_at_tab(tab_id)) for tab_id in tab_ids])

    def start_terminal(self, title: str = None, directory: str = None, command: str = None, clear: bool = False,
                       env: dict[str, str] = None) -> int:
        """Starts a new session with given parameters and returns the session id"""
        session_id = self.add_session()
        session = self.get_session(session_id)

        if title:
            session.title = title
        if directory:
            session.send_text(f'take {directory}\n')
        if env:
            for k, v in env.items():
                session.send_text(f'export {k}=\'{v}\'\n')
        if command:
            session.send_text(f'{command}\n')
        if clear:
            session.send_text('clear\n')

        return session_id

    def get_session(self, session_id: int) -> YakuakeSession:
        """Gets a session object for a given session ID"""
        return YakuakeSession(self.bus, session_id)
