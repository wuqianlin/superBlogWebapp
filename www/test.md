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

Facebook认为MVC无法满足他们的扩展需求，由于他们非常巨大的代码库和庞大的组织，使得MVC很快变得非常复复杂，每当需要添加一项新的功能或特性时，系统的复杂度就成级数增长，致使代码变得脆弱和不可预测，结果导致他们的MVC正在土崩瓦解。认为MVC不适合大规模应用，当系统中有很多的模型和相应的视图时，其复杂度就会迅速扩大，非常难以理解和调试，特别是模型和视图间可能存在的双向数据流动。

``
def api_get_blog(*, id):
    blog = yield from Blog.find(id)
    #comments = yield from Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    comments = yield from Comment.findAll()
    for c in comments:
        c['html_content'] = text2html(c['content'])
``


```
<!-- English -->
<script src="../dist/js/languages/en.js"></script>
<!-- 繁體中文 -->
<script src="../dist/js/languages/zh-tw.js"></script>
```




