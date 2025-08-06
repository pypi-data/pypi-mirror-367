from dsaria.sort import bubble_sort

def test_bubble():
    assert bubble_sort([1,3,4,5,2,6]) == [1,2,3,4,5,6]
    assert bubble_sort([2,4,3,1,9]) == [1,2,3,4,9]