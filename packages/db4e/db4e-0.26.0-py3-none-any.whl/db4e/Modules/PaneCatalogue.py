"""
db4e/Modules/PaneCatalogue.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container

from db4e.Panes.Db4E import Db4E
from db4e.Panes.Donations import Donations
from db4e.Panes.InitialSetup import InitialSetup
from db4e.Panes.Monerod import Monerod
from db4e.Panes.MonerodRemote import MonerodRemote
from db4e.Panes.MonerodType import MonerodType
from db4e.Panes.P2Pool import P2Pool
from db4e.Panes.P2PoolRemote import P2PoolRemote
from db4e.Panes.P2PoolType import P2PoolType
from db4e.Panes.Results import Results
from db4e.Panes.Welcome import Welcome
from db4e.Panes.XMRig import XMRig
from db4e.Panes.XMRig import XMRig


from db4e.Constants.Labels import (
    CONFIG_LABEL, DB4E_LABEL, DB4E_LONG_LABEL, DONATIONS_LABEL, INITIAL_SETUP_LABEL,
    MONEROD_LABEL, MONEROD_REMOTE_LABEL, NEW_LABEL, P2POOL_LABEL, P2POOL_REMOTE_LABEL,
    RESULTS_LABEL, WELCOME_LABEL, XMRIG_LABEL
)
from db4e.Constants.Panes import (
    DB4E_PANE, DONATIONS_PANE, INITIAL_SETUP_PANE, MONEROD_REMOTE_PANE, 
    MONEROD_PANE, MONEROD_TYPE_PANE, P2POOL_PANE, P2POOL_TYPE_PANE, 
    P2POOL_REMOTE_PANE, RESULTS_PANE, WELCOME_PANE, XMRIG_PANE
)

REGISTRY = {
    DB4E_PANE: (Db4E, DB4E_LONG_LABEL, DB4E_LABEL),
    DONATIONS_PANE: (Donations, DONATIONS_LABEL, DONATIONS_LABEL),
    INITIAL_SETUP_PANE: (InitialSetup, DB4E_LONG_LABEL, INITIAL_SETUP_LABEL),
    MONEROD_TYPE_PANE: (MonerodType, MONEROD_LABEL, NEW_LABEL),
    MONEROD_PANE: (Monerod, MONEROD_LABEL, NEW_LABEL),
    MONEROD_REMOTE_PANE: (MonerodRemote, MONEROD_REMOTE_LABEL, CONFIG_LABEL),
    P2POOL_TYPE_PANE: (P2PoolType, P2POOL_LABEL, NEW_LABEL),
    P2POOL_PANE: (P2Pool, P2POOL_LABEL, NEW_LABEL),
    P2POOL_REMOTE_PANE: (P2PoolRemote, P2POOL_REMOTE_LABEL, CONFIG_LABEL),
    XMRIG_PANE: (XMRig, XMRIG_LABEL, NEW_LABEL),
    RESULTS_PANE: (Results, DB4E_LONG_LABEL, RESULTS_LABEL),
    WELCOME_PANE: (Welcome, DB4E_LONG_LABEL, WELCOME_LABEL),
    XMRIG_PANE: (XMRig, XMRIG_LABEL, CONFIG_LABEL),
}

class PaneCatalogue:

    def __init__(self):
        self.registry = REGISTRY

    def get_pane(self, pane_name: str, pane_data=None) -> Container:
        pane_class, _, _ = self.registry[pane_name]
        return pane_class(id=pane_name, data=pane_data) if pane_data else pane_class(id=pane_name)

    def get_metadata(self, pane_name: str) -> tuple[str, str]:
        _, component, msg = self.registry.get(pane_name, (None, "", ""))
        return component, msg