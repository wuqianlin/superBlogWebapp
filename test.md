[TTTOC]

#### Disabled options

- TeX (Based on KaTeX);
- Emoji;
- Task lists;
- HTML tags decode;
- Flowchart and Sequence Diagram;

#### Editor.md directory

    editor.md/
            lib/
            css/
            scss/
            tests/
            fonts/
            images/
            plugins/
            examples/
            languages/     
            editormd.js
            ...

```
python
def api_get_blog(*, id):
    blog = yield from Blog.find(id)

    #comments = yield from Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    comments = yield from Comment.findAll()
    for c in comments:
        c['html_content'] = text2html(c['content'])
```


```html
<!-- English -->
<script src="../dist/js/languages/en.js"></script>

<!-- 繁體中文 -->
<script src="../dist/js/languages/zh-tw.js"></script>
```