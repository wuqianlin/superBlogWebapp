# [译] REST API URI 设计的七准则
在了解 REST API URI 设计的规则之前，让我们快速过一下我们将要讨论的一些术语。

## URI
REST API 使用统一资源标识符（URI）来寻址资源。在今天的网站上，URI 设计范围从可以清楚地传达API的资源模型，如：

http://api.example.com/louvre/leonardo-da-vinci/mona-lisa

到那些难以让人理解的，比如：

http://api.example.com/68dd0-a9d3-11e0-9f1c-0800200c9a66

Tim Berners-Lee 在他的“Web架构公理”列表中列出了关于 URI 的不透明度的注释：

唯一可以使用标识符的是对对象的引用。当你没有取消引用时，你不应该查看 URI 字符串的内容以获取其他信息。 - Tim Berners-Lee

客户端必须遵循 Web 的链接范例，将 URI 视为不透明标识符。

REST API 设计人员应该创建 URI，将 REST API 的资源模型传达给潜在的客户端开发人员。 在这篇文章中，我将尝试为 REST API URsI 引入一套设计规则。

在深入了解规则之前，先看一下在 RFC 3986 中定义的通用 URI 语法，如下所示：

URI = scheme "://" authority "/" path ["?" query] ["#" fragment]

## 规则＃1：URI中不应包含尾随的斜杠（/）
这是作为 URI 路径中最后一个字符的最重要的规则之一，正斜杠（/）不会增加语义值，并可能导致混淆。 REST API 不应该期望有一个尾部的斜杠，并且不应该将它们包含在它们提供给客户端的链接中。

许多 Web 组件和框架将平等对待以下两个 URI：

http://api.canvas.com/shapes/

http://api.canvas.com/shapes

然而，URI 中的每个字符都会被计入作为资源的唯一标识。
两个不同的 URI 映射到两个不同的资源。如果 URI 不同，那么资源也会不同，反之亦然。因此，REST API 必须生成和传达清晰的 URI，并且不应容忍任何客户端尝试去对一个资源进行模糊的标识。

更多的API可能会将客户端重定向到末尾没有斜杠的 URI 上，（他们也可能会返回 301 - 用于重新定位资源的 “Moved Permanently”）。

 ## 规则＃2：正斜杠分隔符（/）必须用于指示层次关系
在 URI 的路径部分的正斜杠（/），用于表示资源之间的层次关系。

例如：

http://api.canvas.com/shapes/polygons/quadrilaterals/squares

## 规则＃3：应使用连字符（ - ）来提高 URI 的可读性
为了使你的 URI 容易被人检索和解释，请使用连字符（ - ）来提高长路径段中名称的可读性。在任何你将使用英文的空格或连字号的地方，在URI中都应该使用连字符来替换。

例如：

http://api.example.com/blogs/guy-levin/posts/this-is-my-first-post

## 规则＃4：不得在 URI 中使用下划线（_）
文本查看器（如浏览器，编辑器等）经常在 URI 下加下划线，以提供可点击的视觉提示。 根据应用程序的字体，下划线（_）字符可能被这个下划线部分地遮蔽或完全隐藏。

为避免这种混淆，请使用连字符（ - ）而不是下划线


## 规则＃5：URI 路径中首选小写字母
方便的话，URI 路径中首选小写字母，因为大写字母有时会导致问题。 RFC 3986 中将 URI 定义为区分大小写，但协议头和域名除外。

例如：

http://api.example.com/my-folder/my-doc

HTTP://API.EXAMPLE.COM/my-folder/my-doc

在 URI 格式规范（RFC 3986）中这两个 URI 是相同的。

http://api.example.com/My-Folder/my-doc

而这个 URI 与上面的两个却是不同的。


## 规则＃6：文件扩展名不应包含在 URI 中
在 Web 上，字符（.）通常用于分隔 URI 的文件名和扩展名。

一个 REST API 不应在 URI 中包含人造的文件扩展名，来表示消息实体的格式。 相反，他们应该通过 header 头中 Content-Type 属性的媒体类型来确定如何处理实体的内容。

http://api.college.com/students/3248234/courses/2005/fall.json

http://api.college.com/students/3248234/courses/2005/fall

不应使用文件扩展名来表示格式偏好。

应鼓励 REST API 客户端使用 HTTP 提供的格式选择机制，即请求 header 中的 Accept 属性。

为了实现简单的链接和调试的便捷，REST API 也可以通过查询参数来支持媒体类型的选择。

## 规则＃7：端点名称是单数还是复数？
这里采用保持简单的原则。虽然你的语法常识会告诉你使用复数来描述资源的单个实例是错误的，但实际的答案是保持 URI 格式一致并且始终使用复数形式。

不必处理奇怪的复数（person/people, goose/geese），这使 API 消费者的生活更美好，也使 API 提供商更容易实现（因为大多数现代框架将在一个通用的 controller 中处理 /students 和 /students/3248234）。

但是你怎么处理关系呢？如果一个关系只能存在于另一个资源中，RESTful 原则可以提供有用的指导。我们来看一下这个例子。某个学生有一些课程。这些课程在逻辑上映射到端点 /students，如下所示：

http://api.college.com/students/3248234/courses - 检索该学生所学习的所有课程清单，学生编号为3248234。

http://api.college.com/students/3248234/courses/physics - 检索该学生的物理课程，学生编号为3248234。

## 结论
当你设计 REST API 服务时，你必须注意资源，这些资源由 URI 定义。

你正在构建的服务中的每个资源，都将至少有一个 URI 来标识它。这个 URI 最好是有意义的，并能充分描述资源。URI 应遵循可预测的层次结构，以增强可理解性，从而提高可用性：可预测的意义在于它们是一致的，层次结构建立在数据具有结构关系的意义上。

RESTful API 是为消费者编写的。URI 的名称和结构应该向消费者传达意义。通过遵循上述规则，你将创建一个更加清晰的 REST API。 这不是一个 REST 规则或约束，而是增强了 API。

也建议你来看看这篇文章，http://blog.restcase.com/5-basic-rest-api-design-guidelines

为你的客户设计，而不是为你的数据。

---

# RESTful API 接口设计整理

## 安全
总是使用 TLS，非 TLS 不重定向，直接返回调用错误 403
无状态认证机制使用 JWT


## URI 的定义
URI 是对一个资源的指向，同一个资源必须使用同一个 URI，不同的资源使用不同的 URI。资源的处理使用动词，GET（查询）、POST（创建）、PUT（全局更新）、PATCH（局部更新）、DELETE（删除）。

请求方式动词 | URI | 注解
---|---|---
GET	| /users | 显示所有用户列表的页面
GET	| /users/{id} | 显示用户个人信息的页面
GET	| /users/create	| 创建用户的页面
POST | /users | 创建用户
GET	| /users/{id}/edit | 编辑用户个人资料的页面
PATCH | /users/{id} | 更新用户
DELETE | /users/{id} | 删除用户


- 使用复数来命名资源，即使资源绝对只有一个
- 路径、参数均要小写
- 路径要为名词，不要为动词
- 路径如果需要多个单词，可以用减号隔开
- 路径中的 /，用于表示资源之间的层次关系
- 参数名称如果需要多个单词，可以用下划线隔开
- URI 末尾不要包含斜杠
- URI 中不包含文件的扩展名

## 查询参数
#### 排序
字段前缀”-“表示降序
```
?sort=-create_time,id
```

#### 过滤
不返回 content,keywords 信息
```
?fields=content,keywords
```

## 版本
三种方式
- HTTP Accepts 头
- URL
- URL 主版本、HTTP 次版本

## Request Headers
Content-Type 为 application/json，否则响应返回 415 Unsupported Media Type

## 状态码
客户端请求错误使用 400 系列状态码，服务端响应错误使用 500 系列状态码。

状态码 | 注解
---|---
200	| 请求资源成功
201 | 同步处理资源的新建或修改成功，返回包含新资源地址的 Location 头
202	| 资源的新建或修改进入异步
204	| 不返回响应主体的成功请求的响应，例如，资源删除成功
206	| 返回了部分资源
400	| 请求格式、参数缺失或者错误
401	| 没有权限
403	| 访问被禁止
404	| 资源不存在
405	| 所请求的 HTTP 方法不允许当前认证用户访问
406	| 请求的数据格式不存在
410	| 资源被永久删除
415	| 请求的媒体类型错误
422	| 请求理解成功，但是参数验证错误
429	| 请求频率超限
500	| 服务器内部错误


## 响应主体
- 全局唯一的小写的 8-4-4-4-12 格式的 UUID，如果嵌套资源，嵌套的资源内依然需要具备一个这样的 UUUID
- 资源的创建时间
- 资源的最后更新时间
- 下一步可用的 URL，客户端不需要关心
- 修改或者创建后，尽量完整的资源详细数据


## 错误
- 唯一的错误码
- 错误信息
- 详细的细节描述


## 自定义 Headers
关于调用频率的一个例子：
```
X-Rate-Limit-Limit：当前时间段内允许的最多请求次数
X-Rate-Limit-Remaining：当前时间段内剩余的请求次数
X-Rate-Limit-Reset：还有多少秒，请求次数限制会被重置
```
目前大部分使用“X-”前缀来区分自定义与非自定义的 HTTP 头，RFC 6848 已经开始废弃这种做法，但目前依然可用。

## 缓存
- ETag
- Last-Modified

## API WIKI 文档要点
- API 文档要与 API 同步更新
- 文档格式的三个部分：请求方式、路径；参数名称、参数类型、参数注解；完整的响应示例

---


## 相关资料

[来自HeroKu的HTTP API 设计指南(中文版)](http://get.ftqq.com/343.get)    
[深入理解 RESTful Api 架构](https://mengkang.net/620.html)    
[理解RESTFul架构](https://mccxj.github.io/blog/20130530_introduce-to-rest.html)    
[[译] REST API URI 设计的七准则](https://github.com/jasonGeng88/blog/blob/master/201706/rest-api.md)    
[RESTful API 设计参考文献列表](https://juejin.im/entry/56a8d5a6d342d300542359af)    
[RESTful API 设计指南](http://www.ruanyifeng.com/blog/2014/05/restful_api.html?bsh_bid=516759003)   
[RESTful API 设计最佳实践](http://blog.jobbole.com/41233/)  
[Best Practices for Designing a Pragmatic RESTful API](https://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api)  
[RESTful API 设计最佳实践-上文翻译](http://blog.jobbole.com/41233/)    
[Principles of good RESTful API Design](https://codeplanet.io/principles-good-restful-api-design/)  
[好RESTful API的设计原则-上文翻译](http://www.cnblogs.com/moonz-wu/p/4211626.html)   
[RESTful API 设计指南-廖雪峰](http://www.ruanyifeng.com/blog/2014/05/restful_api.html?bsh_bid=516759003)  