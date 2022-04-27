from modulefinder import packagePathMap
import eliza


def test_general(): 
    el = eliza.Eliza()
    el.load("doctor.txt")
    assert el.respond("Why?") == "I'm not sure I understand you fully."
    
    
    
    