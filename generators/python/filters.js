// Python Filters.js
'use strict';

Blockly.Python = Blockly.Generator.get('Python');

Blockly.Python.filters = {};

Blockly.Python.addReservedWords('hpf');

Blockly.Python.filters_hpf = function() {

	
	var argument0 = Blockly.Python.valueToCode(this, 'NUM', Blockly.Python.ORDER_ATOMIC) || '0';
/*	if (isNaN(argument0)){
		argument0 = 0;
	}
*/	var code = 'my_hpf(' + argument0 + ')' ;
	var order = code < 0 ? Blockly.Python.ORDER_UNARY_SIGN: Blockly.Python.ORDER_NONE;
	return[code, order];

};

