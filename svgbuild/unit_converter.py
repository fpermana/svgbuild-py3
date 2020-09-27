# -*- coding: utf-8 -*-
#!/usr/bin/env python3

def mm_to_px(value):
    return value * 3.7795275591

def cm_to_px(value):
    return value * 10 * 3.7795275591

def in_to_px(value):
    return value * 96

def pt_to_px(value):
    return value / 3 * 4

def convert_unit(value, unit, target="px"):

    if target == "px":
        if unit == "mm":
            return mm_to_px(value)
        elif unit == "cm":
            return cm_to_px(value)
        elif unit == "in":
            return in_to_px(value)
        elif unit == "pt":
            return pt_to_px(value)
    
    return value
