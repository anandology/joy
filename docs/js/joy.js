
feather.setOptions("joy", {
    mode: "python",
    renderOutput: function(editor, output) {
        var d = JSON.parse(output);
        $(editor).find(".output").text(d.stdout);
        $(editor).find(".output-wrapper div.image").remove();
        $(editor)
            .find(".output-wrapper")
            .append("<div></div>")
            .find("div")
            .addClass("image")
            .html(d.image);
    }
});