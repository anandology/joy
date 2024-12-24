/*

Livecode integration for courses.

To add a livecode example, use the following format.

```{.python .feather}
print("hello, world!")
```

The `python` could be replaced with any of the supported languages.

The supported languages are:
- python
- rust
- html
- golang

To enable instance preview for html examples, add .autopreview to the
header.

```{.html .example .autopreview}
<h1>Heading 1</h1>
<h2>Heading 2</h2>
```
*/

const LIVECODE_BASE_URL = "https://livecode.pipal.in";

const CODEMIRROR_OPTIONS = {
  lineNumbers: true,
  keyMap: "sublime",
  matchBrackets: true,
  indentWithTabs: false,
  tabSize: 4,
  indentUnit: 4,
  extraKeys: {
    Tab: (cm) => {
      cm.somethingSelected()
        ? cm.execCommand('indentMore')
        : cm.execCommand('insertSoftTab');
    }
  }
}

var TEMPLATE = `
<div class="livecode-editor">
  <div class="controls">
    <button class="run">Run</button>
    <div class="labels hidden"></div>
    <span class="run-args-label hidden">Arguments: </span><input type="text" class="run-args hidden" name="args" value="" placeholder="arguments"/>
  </div>

  <div class="filenames" id="file-tabs">
  </div>

  <div class="code-editor">
    <div class="code-wrapper">
      <textarea class="code"></textarea>
    </div>
    <div class="tabs" id="output-tabs">
      <button class="tab-link tab-preview" data-target=".tab-content-preview">Preview</button>
    </div>

    <div class="output-wrapper">
      <div class="spinner" style="display: none;"></div>
      <pre class="output" stype="display: none;"></pre>
    </div>
    <div class="preview tab-content tab-content-preview">
      <iframe frameborder="0" ></iframe>
    </div>
  </div>
</div>
`

function setupExample(feather, element) {
  var editor = {
    element: $(element),
    editor: null,
    codemirror: null,

    options: {
      language: '',
      autopreview: false,
      outputPreview: false,
      multifile: false,
      showArgs: false,
      mode: null,
      runtime: null,
      buttons: [],
      env: {},
      events: {},
      headers: {},
      args: '',
      renderOutput: null // function to render output
    },

    buffers: [],

    outputHooks: [],

    setLabel(label) {
      $(this.editor).find(".labels")
        .show()
        .html(label);
    },

    findLanguage() {
      var languageClass = this.element.find("code").attr("class");
      if (languageClass) {
        return languageClass.replace("language-", "");
      }
      else {
        return "";
      }
    },

    getBuffer(name) {
      for (var i = 0; i < this.buffers.length; i++) {
        if (this.buffers[i].name == name)
          return this.buffers[i];
      }
    },

    selectBuffer(name) {
      var buf = this.getBuffer(name);
      this.codemirror.swapDoc(buf.doc);
      this.codemirror.focus();
    },

    newBuffer(name, text, mode) {
      var doc = CodeMirror.Doc(text, mode);
      var buf = { name: name, doc: doc }
      this.buffers.push(buf);

      this.addFileTab(name);
    },

    prepareBuffers() {
      // codemirror is already setup with current text in <pre>
      var text = this.codemirror.doc.getValue();
      var tokens = text.split(/=== (.*)/);

      // skip the first empty token and move in steps of two
      for (var i = 1; i < tokens.length; i += 2) {
        var filename = tokens[i];
        var code = tokens[i + 1].trim();
        var mode = this.guessFileMode(filename);
        this.newBuffer(filename, code, mode);
      }
      $(this.editor).find(".filenames .file-link:first").addClass('active');
      this.selectBuffer(this.buffers[0].name);
    },

    guessFileMode(filename) {
      if (filename.indexOf(".") == -1) {
        return "htmlmixed";
      }
      var ext = filename.split(".")[1];
      var modes = {
        "py": "python",
        "rs": "rust",
        "html": "htmlmixed",
        "css": "css",
        "js": "javascript",
        "c": "text/x-csrc"
      };
      if (ext in modes) {
        return modes[ext];
      }
      else {
        return ext;
      }
    },

    findModeFromLang(lang) {
      var modes = {
        "py": "python",
        "rs": "rust",
        "html": "htmlmixed",
        "css": "css",
        "js": "javascript",
        "c": "text/x-csrc"
      };
      if (lang in modes) {
        return modes[lang];
      }
      else {
        return lang;
      }
    },

    addFileTab(name) {
      var parent = $(this.editor).find(".filenames");

      $("<button></button>")
        .addClass("file-link")
        .text(name)
        .data("name", name)
        .appendTo(parent);
    },

    triggerEvent(name) {
      if (name in this.options.events) {
        this.options.events[name](this);
      }
    },

    parseOptions() {
      var lang = this.findLanguage();
      var id = $(this.element).data("id") || "default";
      var hasOptions = $(`#livecode-options-${id}`).length > 0;
      var options = hasOptions ? $(`#livecode-options-${id}`).data() : {};

      this.options = {
        ...this.options,
        ...feather.getOptions(lang),
        ...options
      };
      this.options.language = lang;

      if (this.options.renderOutput == null) {
        this.options.renderOutput = this.renderOutputSimple
      }

      if (this.element.hasClass("autopreview")) {
        this.options.autopreview = true;
      }
      else if (this.element.hasClass("no-autopreview")) {
        this.options.autopreview = false;
      }

      if (this.element.hasClass("multi-file")) {
        this.options.multifile = true;
      }

      if ("sourceFile" in this.options) {
        this.options.headers["X-FEATHER-ENTRYPOINT"] = this.options.sourceFile;
      }

      if (this.element.hasClass("show-args")) {
        this.options.showArgs = true;
      }
    },

    getMode() {
      return this.options.mode || this.findModeFromLang(this.options.language);
    },

    getRuntime() {
      return this.options.runtime || this.options.language;
    },


    injectTextArea() {
      var code = $(this.element).text().trim();

      this.element
        .wrap('<div></div>')
        .hide()
        .parent()
        .append(TEMPLATE)
        .find("textarea.code")
        .val(code);
    },

    setupCodeMirror() {
      this.editor = this.element.parent().find(".livecode-editor");
      var textarea = $(this.editor).find("textarea.code")[0];

      var mode = this.getMode();
      var options = { ...CODEMIRROR_OPTIONS, mode: mode };
      console.log("codemirror", options);
      this.codemirror = CodeMirror.fromTextArea(textarea, options);
    },

    setup() {
      this.parseOptions();
      this.injectTextArea();
      this.setupCodeMirror();

      this.addRunButtons();
      this.setupRun();
      this.setupPreview();
      this.setupTabs();

      if (this.options.multifile) {
        this.prepareBuffers();
        this.setupFileTabs();
      }
      this.setupArguments();
      this.triggerEvent("created");
    },

    setupPreview() {
      if (this.options.autopreview) {
        this.setupAutoPreview();
      }
      else if (this.options.outputPreview) {
        this.setupOutputPreview();
      }
      else {
        this.removePreview();
      }
    },
    setupAutoPreview() {
      $(this.editor).find(".controls, .tab-output, .tab-content-output").remove();

      $(this.editor).find(".tab-preview").addClass("active");

      var codemirror = this.codemirror;
      var $iframe = $(this.editor).find(".preview iframe");

      function update() {
        var html = codemirror.doc.getValue();
        $iframe.attr("srcdoc", html);
      }
      codemirror.on("change", update);
      update();
    },

    setupOutputPreview() {
      var $iframe = $(this.editor).find(".preview iframe");

      function update(output) {
        $iframe.attr("srcdoc", output);
      }
      this.outputHooks.push(update);
    },

    removePreview() {
      $(this.editor).find(".tab-preview, .tab-content-preview").remove();
    },

    getEnvHeader() {
      var env = this.options.env;
      if (Object.keys(env).length == 0) {
        return "";
      }
      var value = "";
      for (var k in env) {
        if (value) {
          value += " ";
        }
        value += `${k}=${env[k]}`
      }
      return value;
    },

    getHeaders() {
      var headers = { ...this.options.headers };

      if (Object.keys(this.options.env).length) {
        headers['X-FEATHER-ENV'] = editor.getEnvHeader();
      }
      if (this.options.showArgs) {
        headers['X-FEATHER-ARGS'] = editor.getArguments();
      }
      return headers;
    },

    setupRun() {
      var runtime = this.getRuntime();
      var codemirror = this.codemirror;

      var editor = this;

      $(this.editor).find(".run").on('click', function () {
        var mode = $(this).data("mode") || "exec";
        var body;

        if (editor.options.multifile) {
          body = new FormData();
          for (var i = 0; i < editor.buffers.length; i++) {
            var buf = editor.buffers[i];
            var blob = new Blob([buf.doc.getValue()]);
            body.append(buf.name, blob, buf.name);
          }
        }
        else {
          body = codemirror.doc.getValue();
        }
        var args = editor.getArguments();

        editor.clearOutput();
        editor.showSpinner();

        var url = feather.getLiveCodeURL(runtime);
        if (url != null) {
          fetch(url, {
            method: "POST",
            body: body,
            headers: editor.getHeaders()
          })
            .then(response => response.text())
            .then(output => {
              editor.hideSpinner();
              editor.showOutput(output);
            });
        }
        else {
          editor.showOutput("ERROR: Unable to execute code. The server_url is not configured.");
        }
      });
    },

    setupTabs() {
      var editor = this.editor;
      function updateTabs() {
        var target = $(editor).find(".tab-link.active").data("target");

        $(editor).find(".tab-content").hide();
        $(editor).find(target).show();
      }

      $(function () {
        updateTabs();

        $(editor).find(".tab-link").click(function () {
          $(this).parent().find(".tab-link").removeClass("active");
          $(this).addClass("active");
          updateTabs();
        });
      });
    },
    setupFileTabs() {
      var that = this;
      $(this.editor).find(".filenames").on('click', '.file-link', function () {
        var name = $(this).html();
        that.selectBuffer(name);
        $(this).parent().find(".file-link").removeClass("active");
        $(this).addClass("active");
      });
    },

    setupArguments() {
      if (this.options.showArgs) {
        $(this.editor).find(".run-args")
          .removeClass("hidden")
          .val(this.options.args);
        $(this.editor).find(".run-args-label")
          .removeClass("hidden")
      }
    },

    getArguments() {
      return this.options.showArgs
        ? $(this.editor).find(".run-args").val()
        : "";
    },

    showOutput(output) {
      $(this.editor).find(".output-wrapper .output").show();
      this.options.renderOutput(this.editor, output);

      for (var i = 0; i < this.outputHooks.length; i++) {
        this.outputHooks[i](output);
      }
    },

    // This function is the default value of renderOutput option.
    // shows the output as plain text.
    // It is possible to provide a different implementation to render
    // the output with more styles.
    renderOutputSimple(editor, output) {
      $(editor).find(".output").text(output);
    },

    clearOutput() {
      $(this.editor).find(".output-wrapper .output").hide();
      $(this.editor).find(".output").text("");

      for (var i = 0; i < this.outputHooks.length; i++) {
        this.outputHooks[i]("");
      }
    },

    showSpinner() {
      $(this.editor).find(".output-wrapper .spinner").show();
    },

    hideSpinner() {
      $(this.editor).find(".output-wrapper .spinner").hide();
    },

    // extra run buttons specified in course.js
    addRunButtons() {
      var buttons = this.options.buttons;

      for (var i = 0; i < buttons.length; i++) {
        var b = buttons[i];
        $("<button></button>")
          .addClass("run")
          .data(b.args)
          .html(b.label)
          .appendTo($(this.editor).find(".controls"));
      }
    }
  };

  editor.setup();
  return editor;
}

var feather = {
  editors: [],
  defaultOptions: {
    golang: {
      mode: "go"
    },
    html: {
      mode: "htmlmixed",
      autopreview: true
    }
  },

  options: {},

  isReady() {
    return window.feather_config && window.feather_config.server_url && true;
  },

  getLiveCodeURL(runtime) {
    if (!window.feather_config || !window.feather_config.server_url) {
      return null;
    }
    var livecode_url = window.feather_config.server_url.replace(/\/?$/, '');
    return `${livecode_url}/runtimes/${runtime}`;
  },

  // can set mode, runtime, autopreview etc. for a language.
  setOptions(language, options) {
    this.options[language] = options;
  },

  getOptions(language) {
    var defaults = this.defaultOptions[language] || {};
    var options = this.options[language] || {};
    return { ...defaults, ...options }
  },

  addRunButton(options) {
    this.buttons.push(options);
  },

  setup() {
    var feather = this;
    if (!feather.isReady()) {
      console.log("feature_config is not setup. Livecode functionality may not work.");
    }

    $(function () {
      $("pre.feather").each((i, e) => {
        var editor = setupExample(feather, e);
        feather.editors.push(editor);
      });
    });
  }
};


feather.setup();
