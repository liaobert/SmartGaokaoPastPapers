/**
 * 知识树交互功能
 */

// 切换节点展开/折叠
function toggleNode(element) {
    const node = element.parentElement;
    node.classList.toggle('collapsed');
}

// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
    // 默认展开第一级节点
    const semesterNodes = document.querySelectorAll('.semester-node');
    semesterNodes.forEach((node, index) => {
        if (index === 0) {
            // 第一个学期默认展开
            // node.classList.remove('collapsed');
        } else {
            // 其他默认折叠
            // node.classList.add('collapsed');
        }
    });
    
    // 所有章节默认折叠
    const chapterNodes = document.querySelectorAll('.chapter-node');
    chapterNodes.forEach(node => {
        // node.classList.add('collapsed');
    });
});

// 获取学科图标
function getSubjectIcon(subjectCode) {
    const icons = {
        'chinese': '📖',
        'math': '🔢',
        'english': '🔤',
        'physics': '⚛️',
        'chemistry': '🧪',
        'biology': '🧬',
        'politics': '🏛️',
        'history': '📜',
        'geography': '🌍'
    };
    return icons[subjectCode] || '📚';
}
