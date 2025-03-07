from mpld3 import plugins, utils


class HighlightPiePlugin(plugins.PluginBase):
    JAVASCRIPT = """
    mpld3.register_plugin("highlightPie", HighlightPiePlugin);
    HighlightPiePlugin.prototype = Object.create(mpld3.Plugin.prototype);
    HighlightPiePlugin.prototype.constructor = HighlightPiePlugin;
    HighlightPiePlugin.prototype.requiredProps = ["id", "link"];
    HighlightPiePlugin.prototype.defaultProps = {};

    function HighlightPiePlugin(fig, props) {
        mpld3.Plugin.call(this, fig, props);
    };

    HighlightPiePlugin.prototype.draw = function() {
        var obj = mpld3.get_element(this.props.id);
        console.log(this.props.id);
        var pies = obj.elements();

        // Capture the correct `this` context
        var self = this;

        pies.each(function() {
        var originalFill = d3.select(this).style("fill");
        d3.select(this).attr("original-fill", originalFill);
    });

        pies.on("mouseover", function(d, i) {
            d3.select(this).style("fill", "#ffabdb");
        }).on("mouseout", function(d, i) {
            d3.select(this).style("fill", d3.select(this).attr("original-fill"));
        }).on("click", function(d, i) {
            // Use `self.props` instead of `this.props`
            window.location.href = self.props.link;
        });
    };
    """

    def __init__(self, Pie, link):
        self.dict_ = {"type": "highlightPie", "id": utils.get_id(Pie), "link": link}
