import dsaria.sort
import pytest

def test_counting_sort_normal_case():
    arr = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    assert dsaria.sort.counting_sort(arr=arr) == sorted(arr)

def test_counting_sort_empty_list():
    assert dsaria.sort.counting_sort(arr=[]) == []

def test_counting_sort_single_element():
    assert dsaria.sort.counting_sort(arr=[42]) == [42]

def test_counting_sort_duplicates():
    arr = [2, 3, 2, 1, 4, 1, 1]
    assert dsaria.sort.counting_sort(arr=arr) == sorted(arr)

def test_counting_sort_negative_raises_value_error():
    with pytest.raises(ValueError):
        dsaria.sort.counting_sort(arr=[1, 2, -3])

def test_counting_sort_float_raises_type_error():
    with pytest.raises(TypeError):
        dsaria.sort.counting_sort(arr=[1, 2, 3.5])  # type: ignore

def test_counting_sort_string_raises_type_error():
    with pytest.raises(TypeError):
        dsaria.sort.counting_sort(arr=[1, 2, "3"])  # type: ignore