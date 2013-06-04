Blockly.Language.filters_hpf = {
  helpUrl: 'http://www.example.com/',
  init: function() {
    this.setColour(290);
    this.appendValueInput("NAME")
        .setCheck("Number")
        .appendTitle("My HPF");
    this.setOutput(true, "Number");
    this.setTooltip('');
  }
};
