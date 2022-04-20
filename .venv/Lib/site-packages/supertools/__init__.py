def superable(cls) :
    '''Provide .__super in python 2.x classes without having to specify the current 
    class name each time super is used (DRY principle).'''
    name = cls.__name__
    super_name = '_%s__super' % (name,)
    setattr(cls,super_name,super(cls))
    return cls

