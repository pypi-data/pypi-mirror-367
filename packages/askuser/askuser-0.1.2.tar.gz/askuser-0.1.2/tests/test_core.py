import pytest
from askuser.core import (
    validate_input, pretty_menu, validate_user_option,
    validate_user_option_value, validate_user_option_enumerated,
    choose_from_db, choose_dict_from_list_of_dicts, yes
)


def setup_input(monkeypatch, inputs):
    gen = (i for i in inputs)
    # Patch input_white and print_blue to avoid real console IO
    monkeypatch.setattr('askuser.core.input_white', lambda prompt: next(gen))
    monkeypatch.setattr('askuser.core.print_blue', lambda *args, **kwargs: None)


def test_validate_input_int(monkeypatch):
    setup_input(monkeypatch, ['42'])
    assert validate_input('Enter number', 'int') == 42


def test_validate_input_default(monkeypatch):
    setup_input(monkeypatch, [''])
    assert validate_input('Enter number', 'int', default=7) == 7


def test_validate_input_custom(monkeypatch):
    setup_input(monkeypatch, ['usd'])
    assert validate_input('Currency?', 'custom', expected_inputs=['usd', 'eur']) == 'usd'


def test_validate_input_not_in(monkeypatch):
    setup_input(monkeypatch, ['new'])
    assert validate_input('Value?', 'not_in', not_in=['old', 'existing']) == 'new'


def test_yes_function(monkeypatch):
    setup_input(monkeypatch, ['y'])
    assert yes('Continue?') is True
    setup_input(monkeypatch, ['n'])
    assert yes('Continue?') is False


def test_validate_user_option(monkeypatch):
    setup_input(monkeypatch, ['0'])
    # q is auto-added
    key = validate_user_option('Pick', 'A', 'B')
    assert key == '0'


def test_validate_user_option_no_quit(monkeypatch):
    setup_input(monkeypatch, ['1'])
    # suppress quit
    key = validate_user_option('Pick', 'X', 'Y', q=False)
    assert key == '1'


def test_validate_user_option_value(monkeypatch):
    setup_input(monkeypatch, ['b'])
    val = validate_user_option_value(a='Alpha', b='Beta', c='Gamma')
    assert val == 'Beta'


def test_validate_user_option_enumerated(monkeypatch):
    setup_input(monkeypatch, ['2'])
    key, val = validate_user_option_enumerated({10: 'Ten', 20: 'Twenty'}, start=1)
    assert (key, val)  == (10, 'Ten')


def test_choose_from_db(monkeypatch):
    data = [{'id': 1, 'name': 'One'}, {'id': 2, 'name': 'Two'}]
    setup_input(monkeypatch, ['2'])
    idx, row = choose_from_db(data)
    assert idx == 2 and row['name'] == 'Two'


def test_choose_from_db_xq(monkeypatch):
    data = [{'id': 1, 'name': 'One'}]
    setup_input(monkeypatch, ['xq'])
    idx, val = choose_from_db(data, xq=True)
    assert idx == 'xq' and val == 'quit'


def test_choose_dict_from_list_of_dicts(monkeypatch):
    # Monkeypatch validate_user_option to return key directly
    monkeypatch.setattr('askuser.core.validate_user_option', lambda msg, **kwargs: 'Banana')
    fruits = [{'name': 'Apple', 'color': 'red'}, {'name': 'Banana', 'color': 'yellow'}]
    chosen = choose_dict_from_list_of_dicts(fruits, 'name')
    assert chosen['color'] == 'yellow'
