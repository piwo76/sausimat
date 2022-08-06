import pytest

from sausimat.sausimat import Sausimat
from mock import patch


class TestAction:
    @pytest.mark.parametrize('action_str, mock_func', [
        ('{"card": null}', 'card_removed'),
        ('{"card": "C1 13 AD 5F"}', 'new_card'),
        ('{"volume": 30}', 'set_volume'),
        ('{"button": 0}', 'next'),
        ('{"button": 1}', 'previous'),
        ('{"button": 2}', 'shutdown'),
        ('{asdd', None),
    ])
    def test_action(self, action_str, mock_func):

        with patch('serial.Serial'):
            with patch('sausimat.mopidy.SausimatMopidy.connect'):
                if mock_func:
                    with patch(f'sausimat.sausimat.Sausimat.{mock_func}') as mock_func:
                        sausimat = Sausimat()
                        sausimat.perform_action(action_str)
                        assert mock_func.call_count > 0
                else:
                    sausimat = Sausimat()
                    sausimat.perform_action(action_str)
