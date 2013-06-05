Blockly.Language.filters_hpf = {
  helpUrl: 'http://www.example.com/',
  init: function() {
    this.setColour(290);
    this.appendValueInput("NUM")
        //.setCheck("null")
        .appendTitle("My HPF");
    this.setOutput(true, "null");
    this.setTooltip('');
  }
};
