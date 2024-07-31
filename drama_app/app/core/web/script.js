let nodeCount = 0;
const nodesList = [];

function addNode() {
    nodeCount++;
    const nodeDiv = document.createElement('div');
    nodeDiv.classList.add('node');
    nodeDiv.setAttribute('draggable', true);
    nodeDiv.setAttribute('id', `node${nodeCount}`);
    nodeDiv.ondragstart = dragStart;
    nodeDiv.ondragover = allowDrop;
    nodeDiv.ondrop = drop;
    nodeDiv.innerHTML = `
        <h2 onclick="toggleNodeContent(${nodeCount})">
            节点 ${nodeCount} <span id="toggleIcon${nodeCount}">+</span>
        </h2>
        <div class="node-content" id="nodeContent${nodeCount}">
            <label for="nodeId${nodeCount}">节点ID</label>
            <input type="text" id="nodeId${nodeCount}" placeholder="例如：a0">
            <label for="role${nodeCount}">角色</label>
            <input type="text" id="role${nodeCount}" placeholder="例如：法官">
            <label for="action${nodeCount}">行动</label>
            <input type="text" id="action${nodeCount}" placeholder="例如：开庭">
            <label for="defaultNext${nodeCount}">默认下一个节点</label>
            <select id="defaultNext${nodeCount}" onchange="autoFillNode(${nodeCount})">
                <option value="">选择下一个节点</option>
            </select>
            <div id="nextActions${nodeCount}">
                <label>后续动作</label>
                <div class="nextAction">
                    <input type="text" placeholder="动作名称（例如：继续）">
                    <select onchange="autoFillNextAction(this)">
                        <option value="">选择下一个节点</option>
                    </select>
                    <input type="text" placeholder="角色">
                    <input type="text" placeholder="行动">
                    <button type="button" class="delete-action" onclick="deleteNextAction(this)">删除</button>
                </div>
            </div>
            <button type="button" onclick="addNextAction(${nodeCount})">添加后续动作</button>
            <button type="button" onclick="saveNode(${nodeCount})">保存节点</button>
        </div>
    `;
    document.getElementById('nodes').appendChild(nodeDiv);
    updateNodeList();
}

function toggleNodeContent(nodeIndex) {
    const contentDiv = document.getElementById(`nodeContent${nodeIndex}`);
    const toggleIcon = document.getElementById(`toggleIcon${nodeIndex}`);
    const nodeId = document.getElementById(`nodeId${nodeIndex}`).value;
    const role = document.getElementById(`role${nodeIndex}`).value;
    const action = document.getElementById(`action${nodeIndex}`).value;

    if (contentDiv.style.display === 'none') {
        contentDiv.style.display = 'block';
        toggleIcon.textContent = '-';
    } else {
        contentDiv.style.display = 'none';
        toggleIcon.textContent = `+ (节点ID: ${nodeId}, 角色: ${role}, 行动: ${action})`;
    }
}

function addNextAction(nodeIndex) {
    const nextActionsDiv = document.getElementById(`nextActions${nodeIndex}`);
    const nextActionDiv = document.createElement('div');
    nextActionDiv.classList.add('nextAction');
    nextActionDiv.innerHTML = `
        <input type="text" placeholder="动作名称（例如：继续）">
        <select onchange="autoFillNextAction(this)">
            <option value="">选择下一个节点</option>
        </select>
        <input type="text" placeholder="角色">
        <input type="text" placeholder="行动">
        <button type="button" class="delete-action" onclick="deleteNextAction(this)">删除</button>
    `;
    nextActionsDiv.appendChild(nextActionDiv);
    updateNodeList();
}

function deleteNextAction(button) {
    const nextActionDiv = button.parentElement;
    nextActionDiv.parentElement.removeChild(nextActionDiv);
}

function updateNodeList() {
    nodesList.length = 0;
    for (let i = 1; i <= nodeCount; i++) {
        const nodeId = document.getElementById(`nodeId${i}`).value;
        if (nodeId) {
            nodesList.push(nodeId);
        }
    }

    for (let i = 1; i <= nodeCount; i++) {
        const defaultNextSelect = document.getElementById(`defaultNext${i}`);
        const nextActionsDiv = document.getElementById(`nextActions${i}`);
        updateSelectOptions(defaultNextSelect);

        const nextActions = nextActionsDiv.getElementsByTagName('select');
        for (const select of nextActions) {
            updateSelectOptions(select);
        }
    }
}

function updateSelectOptions(select) {
    const selectedValue = select.value;
    select.innerHTML = '<option value="">选择下一个节点</option>';
    for (const nodeId of nodesList) {
        const option = document.createElement('option');
        option.value = nodeId;
        option.textContent = nodeId;
        if (nodeId === selectedValue) {
            option.selected = true;
        }
        select.appendChild(option);
    }
}

function autoFillNode(nodeIndex) {
    const select = document.getElementById(`defaultNext${nodeIndex}`);
    const selectedNodeId = select.value;
    if (selectedNodeId) {
        const nodeData = getNodeData(selectedNodeId);
        document.getElementById(`role${nodeIndex}`).value = nodeData.role;
        document.getElementById(`action${nodeIndex}`).value = nodeData.action;
    }
}

function autoFillNextAction(select) {
    const selectedNodeId = select.value;
    if (selectedNodeId) {
        const nextActionDiv = select.parentElement;
        const nodeData = getNodeData(selectedNodeId);
        const roleInput = nextActionDiv.querySelector('input:nth-child(4)');
        const actionInput = nextActionDiv.querySelector('input:nth-child(6)');

        if (!roleInput.value) {
            roleInput.value = nodeData.role;
        }
        if (!actionInput.value) {
            actionInput.value = nodeData.action;
        }
    }
}

function getNodeData(nodeId) {
    for (let i = 1; i <= nodeCount; i++) {
        const currentId = document.getElementById(`nodeId${i}`).value;
        if (currentId === nodeId) {
            const role = document.getElementById(`role${i}`).value;
            const action = document.getElementById(`action${i}`).value;
            return { role, action };
        }
    }
    return {};
}

function saveNode(nodeIndex) {
    const nodeId = document.getElementById(`nodeId${nodeIndex}`).value;
    if (!nodeId) {
        alert('节点ID不能为空');
        return;
    }
    updateNodeList();
    alert(`节点 ${nodeId} 保存成功`);
    toggleNodeContent(nodeIndex); // 保存后折叠
}


function generateJSON() {
    const nodes = {};
    for (let i = 1; i <= nodeCount; i++) {
        const nodeId = document.getElementById(`nodeId${i}`).value;
        const role = document.getElementById(`role${i}`).value;
        const action = document.getElementById(`action${i}`).value;
        const defaultNext = document.getElementById(`defaultNext${i}`).value;
        const nextActions = Array.from(document.getElementById(`nextActions${i}`).getElementsByClassName('nextAction'));

        const next = {};
        nextActions.forEach(actionDiv => {
            const inputs = actionDiv.getElementsByTagName('input');
            const select = actionDiv.getElementsByTagName('select')[0];
            const actionName = inputs[0].value;
            next[actionName] = {
                next_node: select.value,
                role: inputs[1].value,
                action: inputs[2].value
            };
        });

        nodes[nodeId] = {
            role: role,
            action: action,
            next: next,
            default_next: defaultNext
        };
    }

    document.getElementById('output').value = JSON.stringify(nodes, null, 4);
}

let dragged;

function dragStart(event) {
    dragged = event.target;
    event.target.style.opacity = 0.5;
}

function dragEnd(event) {
    event.target.style.opacity = "";
}

function allowDrop(event) {
    event.preventDefault();
}

function drop(event) {
    event.preventDefault();
    if (event.target.className === "container" || event.target.className === "node") {
        dragged.parentNode.removeChild(dragged);
        event.target.appendChild(dragged);
    }
}
