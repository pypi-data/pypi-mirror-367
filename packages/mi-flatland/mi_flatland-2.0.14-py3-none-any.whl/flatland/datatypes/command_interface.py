"""
command_interface.py
"""

from collections import namedtuple

New_Compartment = namedtuple('New_Compartment', 'content expansion')
"""
User specification of a compartment's text content and any vertical expansion

    Attributes
    
    - content -- (list (str))  A list of strings to be rendered starting from the first string and moving downward
    - expansion -- (float > 1) Multiple the height of this compartment by this factor to increase its size
"""

New_Stem = namedtuple('New_Stem', 'stem_position semantic node face anchor stem_name')
"""
User specification of a Stem in a Tree Connector

    Attributes
    
    - stem_position -- (str) Name of stem position such as 'class mult' or 'generalization'
    - semantic -- (str) Name of semantic such as '1 mult' or 'superclass'
    - node -- (Node) Node object
    - face -- (NodeFace)
    - anchor -- (int) AnchorPosition
    - stem_name -- (StemName) Name specification associated with the stem such as class model verb phrase
"""
New_Trunk_Branch = namedtuple('New_Branch', 'path graft trunk_stem leaf_stems floating_leaf_stem')
"""
User specification of the Branch of a Tree Connector that includes the Trunk Stem

    Attributes
    
    - path -- The Lane/Rut where this Branch is positioned
    - graft -- Optional grafting New Stem
    - leaf_stems -- All New Stem leaves in this offshoot Branch
    - floating_leaf_stem -- If a graft is specified, this New Stem floats on the other side of it
"""
New_Offshoot_Branch = namedtuple('New_Branch', 'path graft leaf_stems floating_leaf_stem')
"""
User specification of a Branch of a Tree Connector that does not include the Trunk Stem

    Attributes
    
    - path -- The Lane/Rut where this Branch is positioned
    - graft -- Optional grafting New Stem
    - leaf_stems -- All New Stem leaves in this offshoot Branch
    - floating_leaf_stem -- If a graft is specified, this New Stem floats on the other side of it
"""
New_Branch_Set = namedtuple('New_Branch_Set', 'trunk_branch offshoot_branches')
"""
User specification of a complete set of Branches in a Tree Connector

    Attributes
    
    - trunk_branch -- Branch connecting the Trunk Stem
    - offshoot_branches -- Optional Branches sprouting off the Trunk Stem's Branch
"""
New_Path = namedtuple('New_Path', 'lane rut')
"""
User specification of a Branch Path

    Attributes
    
    - lane -- row or column number
    - rut -- position within the lane
"""