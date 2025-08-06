from qbrick_alias import AliasManager
from pysr_container.definitions import Object


definitions = {
    AliasManager: Object(AliasManager, single_instance=True)
}
