from mpld3 import plugins, utils


class HighlightBarPlugin(plugins.PluginBase):
    JAVASCRIPT = """
    mpld3.register_plugin("highlightbar", HighlightBarPlugin);
    HighlightBarPlugin.prototype = Object.create(mpld3.Plugin.prototype);
    HighlightBarPlugin.prototype.constructor = HighlightBarPlugin;
    HighlightBarPlugin.prototype.requiredProps = ["id"];
    HighlightBarPlugin.prototype.defaultProps = {};

    function HighlightBarPlugin(fig, props) {
        mpld3.Plugin.call(this, fig, props);
    };

    HighlightBarPlugin.prototype.draw = function() {
        var obj = mpld3.get_element(this.props.id);
        console.log(obj);
        var bars = obj.elements();
        console.log(bars);

        bars.on("mouseover", function(d, i) {
            d3.select(this).style("fill", "orange");
        }).on("mouseout", function(d, i) {
            d3.select(this).style("fill", "skyblue");
        });
    };
    """

    def __init__(self, bar):
        self.dict_ = {"type": "highlightbar", "id": utils.get_id(bar)}
