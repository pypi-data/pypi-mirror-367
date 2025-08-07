from typing import List, Any

def bubble_sort(arr: List[Any]) -> List[Any]:
    """
    Sorts a list in ascending order using the bubble sort algorithm.

    Parameters:
    arr (list): A list of comparable elements (e.g., integers or floats). 
    If you're passing in a list of objects, make sure that the comparison methods, such as __gt__(self, other), are defined.

    Returns:
    list: The sorted list in ascending order.

    Example:
    >>> bubble_sort([3, 1, 2])
    [1, 2, 3]
    """
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

    return arr