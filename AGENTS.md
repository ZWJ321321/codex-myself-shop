# AGENTS 说明

本目录现在是一个基于 **Vue 3 + Vite** 的餐厅介绍页项目，不再是纯静态 `html/css/js` 结构。

## 项目结构

- `index.html`：项目入口文件。
  - 在开发环境下由 Vite 注入并加载 `src/main.js`。
  - 当用户直接用 `file://` 打开根目录 `index.html` 时，会跳转到 `dist/index.html`。
- `src/App.vue`：页面主结构，包含首屏、品牌故事、招牌菜、空间环境、亮点、联系信息等区块。
- `src/styles.css`：完整视觉样式，包含配色变量、响应式布局、悬浮态、滚动导航、入场动画。
- `src/ui.js`：页面交互辅助函数，负责滚动导航状态与区块渐入逻辑。
- `src/main.js`：Vue 挂载入口。
- `vite.config.js`：Vite 配置，当前使用相对 `base`，以便构建后资源可从 `dist/` 相对路径加载。
- `page.test.mjs`：基础校验测试，检查 Vue 入口、页面区块、样式关键选择器和交互 helper 是否正常。
- `dist/`：构建产物目录，由 `npm run build` 生成，不纳入版本控制。

## 修改建议

- 这是模板型页面，优先直接替换文案、联系方式、营业时间、地址、品牌名，不要先重做结构。
- 如需继续组件化，优先从 `src/App.vue` 中拆出语义明确的区块组件，例如 Hero、菜品区、联系区；不要为了拆分而拆分。
- 如果要换成真实餐厅素材，优先替换 `src/App.vue` 中的占位文案，以及 `src/styles.css` 中用渐变模拟图片的区域。
- 当前视觉风格是暖色、木质、晚餐氛围，后续修改应尽量保持整体调性一致。

## 验证方式

- 运行测试：`node --test .\page.test.mjs`
- 运行开发环境：`npm run dev`
- 运行生产构建：`npm run build`
- 本地预览构建结果：`npm run preview`

修改完成后，至少检查：

- 页面是否能在 `npm run dev` 下正常显示
- `npm run build` 是否成功
- 首屏导航是否正常跳转
- 滚动后导航是否出现 `is-scrolled` 状态
- 各区块是否仍有渐入效果
- 移动端宽度下布局是否没有明显错位

## 注意事项

- 项目内容以中文为主，编辑时保持 UTF-8 编码，避免中文文案乱码。
- `src/ui.js` 中的 `isScrolled` 仍被测试直接引用，改动时不要破坏这个导出约定。
- `node_modules/`、`dist/`、`.idea/`、`preview*.png` 已在 `.gitignore` 中忽略，不要手动加入版本控制。
- 若只是更新餐厅信息，尽量做最小改动，避免把模板中已有的响应式和动画一并改坏。

## 最近一次发布记录

- 工作区 `E:\餐厅介绍` 已从纯静态页迁移为 Vue 3 + Vite 项目。
- 已验证命令：
  - `node --test .\page.test.mjs`
  - `npm run build`
- GitHub 仓库：`ZWJ321321/codex-myself-shop`
- 发布分支：`codex/migrate-restaurant-page-to-vue`
- Draft PR：`https://github.com/ZWJ321321/codex-myself-shop/pull/1`
