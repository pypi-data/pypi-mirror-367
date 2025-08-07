from . import *
unit_registry=pint.UnitRegistry()

def volume():
	height=Prompt.__init2__(None,func=FormBuilderMkText,ptext="height?: ",helpText="height=1",data="dec.dec")
	if height is None:
		return
	elif height in ['d',]:
		height=Decimal('1')
	
	width=Prompt.__init2__(None,func=FormBuilderMkText,ptext="width?: ",helpText="width=1 ",data="dec.dec")
	if width is None:
		return
	elif width in ['d',]:
		width=Decimal('1')
	


	length=Prompt.__init2__(None,func=FormBuilderMkText,ptext="length?: ",helpText="length=1",data="dec.dec")
	if length is None:
		return
	elif length in ['d',]:
		length=Decimal('1')

	return length*width*height

def volume_pint():
	height=Prompt.__init2__(None,func=FormBuilderMkText,ptext="height?: ",helpText="height=1",data="string")
	if height is None:
		return
	elif height in ['d',]:
		height='1'
	
	width=Prompt.__init2__(None,func=FormBuilderMkText,ptext="width?: ",helpText="width=1 ",data="string")
	if width is None:
		return
	elif width in ['d',]:
		width='1'
	


	length=Prompt.__init2__(None,func=FormBuilderMkText,ptext="length?: ",helpText="length=1",data="string")
	if length is None:
		return
	elif length in ['d',]:
		length='1'

	return unit_registry.Quantity(length)*unit_registry.Quantity(width)*unit_registry.Quantity(height)
	
preloader={
	f'{uuid1()}':{
						'cmds':['volume',],
						'desc':f'find the volume of height*width*length without dimensions',
						'exec':volume
					},
	f'{uuid1()}':{
						'cmds':['volume pint',],
						'desc':f'find the volume of height*width*length using pint to normalize the values',
						'exec':volume_pint
					},
}