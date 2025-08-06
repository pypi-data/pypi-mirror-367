(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports, require('@beanbag/spina')) :
    typeof define === 'function' && define.amd ? define(['exports', '@beanbag/spina'], factory) :
    (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global.RBIntegrationsExtension = global.RBIntegrationsExtension || {}, global.Spina));
})(this, (function (exports, spina) { 'use strict';

    var _class, _dec, _class2;


    /**
     * An inline editor view for selecting Asana tasks.
     */
    let AsanaInlineEditorView = spina.spina(_class = class AsanaInlineEditorView extends RB.InlineEditorView {
      /**
       * Initialize the view.
       *
       * Args:
       *     options (object):
       *         Options for the view.
       */
      initialize(options) {
        options = _.defaults(options, {
          hasRawValue: true,
          formatResult: value => {
            if (value && value.name) {
              return value.name.htmlEncode();
            } else {
              return '';
            }
          },
          getFieldValue: editor => {
            const selectize = this.$field[0].selectize;
            const selected = selectize.getValue();
            return JSON.stringify(selected.map(key => _.pick(selectize.options[key], ['completed', 'gid', 'workspace_id', 'name'])));
          },
          isFieldDirty: (editor, initialValue) => {
            const value = editor.getValue();
            return initialValue !== value;
          },
          setFieldValue: (editor, value) => {
            // This is a no-op, since we do this in the $.selectize call.
          }
        });
        super.initialize(options);
      }

      /**
       * Create and return the field to use for the input element.
       *
       * Returns:
       *     jQuery:
       *     The newly created input element.
       */
      createField() {
        return $('<select multiple class="asana-field">');
      }

      /**
       * Connect events.
       */
      setupEvents() {
        super.setupEvents();
        this.$field.on('change', this._scheduleUpdateDirtyState.bind(this));
      }

      /**
       * Show the editor.
       *
       * Args:
       *     options (object, optional):
       *         Options for showing the editor.
       */
      showEditor(options = {}) {
        super.showEditor(options);
        if (this.options.focusOnOpen) {
          this.$field[0].selectize.focus();
        }
      }
    }) || _class;
    /**
     * A task entry in the selector.
     *
     * Version Added:
     *     4.0.1
     */
    /**
     * The response from the Asana task query URL.
     *
     * Version Added:
     *     4.0.1
     */
    /**
     * A review request field view for selecting Asana tasks.
     */
    let AsanaFieldView = (_dec = spina.spina({
      prototypeAttrs: ['taskTemplate']
    }), _dec(_class2 = class AsanaFieldView extends RB.ReviewRequestFields.TextFieldView {
      static autocomplete = {};
      static multiline = true;
      static useEditIconOnly = true;
      static taskTemplate = _.template(`<<%- tagName %> class="asana-task<% if (completed) { %> completed<% } %>">
 <a href="https://app.asana.com/0/<%- workspaceId %>/<%- taskId %>/">
  <div class="asana-task-checkbox">
   <svg viewBox="0 0 32 32">'
    <polygon points="27.672,4.786 10.901,21.557 4.328,14.984 1.5,17.812 10.901,27.214 30.5,7.615"></polygon>
   </svg>
  </div>
  <span><%- taskSummary %></span>
 </a>
</<%- tagName %>>`);
      /**
       * Format the contents of the field.
       *
       * This will apply the contents of the model attribute to the field
       * element. If the field defines a ``formatValue`` method, this will use
       * that to do the formatting. Otherwise, the element will just be set to
       * contain the text of the value.
       */
      _formatField() {
        const fieldName = this.jsonFieldName || this.fieldID;
        const opts = {
          useExtraData: this.useExtraData
        };
        const tasks = JSON.parse(this.model.getDraftField(fieldName, opts));
        this._renderValue(tasks);
      }

      /**
       * Render the current value of the field.
       *
       * Args:
       *     tasks (Array of object):
       *         The current value of the field.
       */
      _renderValue(tasks) {
        const lis = tasks.map(task => this.taskTemplate({
          completed: task.completed,
          workspaceId: task.workspace_id,
          taskId: task.gid,
          taskSummary: task.name,
          tagName: 'li'
        }));
        this.$el.html(`<ul>${lis.join('')}</ul>`);
      }

      /**
       * Return the type to use for the inline editor view.
       *
       * Returns:
       *     function:
       *     The constructor for the inline editor class to instantiate.
       */
      _getInlineEditorClass() {
        return AsanaInlineEditorView;
      }

      /**
       * Add auto-complete functionality to the field.
       */
      _buildAutoComplete() {
        const reviewRequest = this.model.get('reviewRequest');
        const localSite = reviewRequest.get('localSitePrefix');
        const reviewRequestId = reviewRequest.get('id');
        const url = `${SITE_ROOT}rbintegrations/asana/${localSite}task-search/${reviewRequestId}/`;
        const $field = this.inlineEditorView.$field;
        const tasks = this.$el.data('raw-value') || [];
        tasks.forEach(task => {
          if (task.gid === undefined) {
            task.gid = String(task.id);
          }
        });
        this._renderValue(tasks);
        $field.selectize({
          copyClassesToDropdown: true,
          dropdownParent: 'body',
          labelField: 'name',
          valueField: 'gid',
          multiple: true,
          options: tasks,
          items: tasks.map(task => task.gid),
          optgroupLabelField: 'workspace',
          searchField: 'name',
          sortField: [{
            'field': 'completed'
          }, {
            'field': 'name'
          }],
          render: {
            option: data => {
              return this.taskTemplate({
                completed: data.completed,
                workspaceId: data.workspace_id,
                taskId: data.gid,
                taskSummary: data.name,
                tagName: 'div'
              });
            }
          },
          load(query, callback) {
            const params = new URLSearchParams();
            params.append('q', query);
            fetch(`${url}?${params.toString()}`).then(rsp => rsp.json()).then(rsp => {
              const items = [];
              this.clearOptionGroups();
              for (const group of rsp) {
                this.addOptionGroup(group.workspace, group);
                for (let j = 0; j < group.tasks.length; j++) {
                  const task = group.tasks[j];
                  task.optgroup = group.workspace;
                  task.workspace_id = group.workspace_id;
                  const notesLines = task.notes.split('\n');
                  task.notes = notesLines.splice(8).join('\n');
                  items.push(task);
                }
              }
              this.refreshOptions();
              callback(items);
            }).catch(err => {
              console.error('Unable to fetch Asana tasks:', err);
              callback();
            });
          }
        });
      }
    }) || _class2);

    exports.AsanaFieldView = AsanaFieldView;

    Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

}));
//# sourceMappingURL=index.js.map
