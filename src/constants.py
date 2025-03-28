from enum import Enum

class SomeType(str, Enum): 
    SOME_VALUE = "some_value"
    SOME_OTHER_VALUE = "some_other_value"

class SomeOtherType(str, Enum): 
    SOME_VALUE = "some_value"
    SOME_OTHER_VALUE = "some_other_value"