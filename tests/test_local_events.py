from requeue.models import QueueEvent

from local import CommandConfig


def test_command_config_find_donate_command():
    """Test finding a donate command based on message and price"""
    # Setup test commands
    test_commands = [
        {
            'name': 'test_donate',
            'price': 100,
            'type': 'donate',
            'command': 'test_donate_script.py',
        }
    ]

    # Setup currencies
    currencies = {
        'USD': 80,
        'RUB': 1,
        'EUR': 90,
        'POINTS': 1,
    }

    # Initialize CommandConfig
    config = CommandConfig(currencices=currencies, lcommands=test_commands)

    # Create a test event that should match
    event = QueueEvent(
        message='test_donate thank you!',
        amount=150,  # Higher than price
        billing_system='DONATIONALERTS',  # Not TWITCH
        currency='RUB',
        event_type='donate',
    )

    # Test that the command is found
    result = config.find(event)
    assert result == 'test_donate_script.py'


def test_command_config_find_twitch_command():
    """Test finding a twitch command"""
    # Setup test commands
    test_commands = [
        {
            'name': '!test',
            'price': 0,
            'type': 'twitch',
            'command': 'test_twitch_script.py',
        }
    ]

    # Setup currencies
    currencies = {
        'USD': 80,
        'RUB': 1,
        'EUR': 90,
        'POINTS': 1,
    }

    # Initialize CommandConfig
    config = CommandConfig(currencices=currencies, lcommands=test_commands)

    # Create a test event that should match
    event = QueueEvent(
        message='!test',
        amount=0,
        billing_system='RETWITCH',
        currency='RUB',
        event_type='twitch',
    )

    # Test that the command is found
    result = config.find(event)
    assert result == 'test_twitch_script.py'


def test_command_config_find_bycash_command():
    """Test finding a bycash command"""
    # Setup test commands
    test_commands = [
        {
            'name': '',
            'price': 50,
            'type': 'bycash',
            'command': 'test_bycash_script.py',
        }
    ]

    # Setup currencies
    currencies = {
        'USD': 80,
        'RUB': 1,
        'EUR': 90,
        'POINTS': 1,
    }

    # Initialize CommandConfig
    config = CommandConfig(currencices=currencies, lcommands=test_commands)

    # Create a test event that should match
    event = QueueEvent(
        message='', amount=50, billing_system='ANY', currency='RUB', event_type='bycash'
    )

    # Test that the command is found
    result = config.find(event)
    assert result == 'test_bycash_script.py'


def test_command_config_no_match():
    """Test that no command is found when there's no match"""
    # Setup test commands
    test_commands = [
        {
            'name': 'test_donate',
            'price': 100,
            'type': 'donate',
            'command': 'test_donate_script.py',
        }
    ]

    # Setup currencies
    currencies = {
        'USD': 80,
        'RUB': 1,
        'EUR': 90,
        'POINTS': 1,
    }

    # Initialize CommandConfig
    config = CommandConfig(currencices=currencies, lcommands=test_commands)

    # Create a test event that should NOT match (amount is less than price)
    event = QueueEvent(
        message='test_donate thank you!',
        amount=50,  # Less than price
        billing_system='DONATIONALERTS',
        currency='RUB',
        event_type='donate',
    )

    # Test that no command is found
    result = config.find(event)
    assert result is None
