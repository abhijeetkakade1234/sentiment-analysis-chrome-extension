chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'TRIGGER_EXTRACTION') {
        console.log('Triggering extractAndSendContent');
        extractAndSendContent();
    }
});

function extractAndSendContent() {
    const extracted = extractCleanContent();
    console.log('Extracted blocks:', extracted);

    try {
        chrome.runtime.sendMessage({
            type: 'EXTRACTED_TEXT_BLOCKS',
            blocks: extracted.map(x => x.text)
        });
    } catch (err) {
        console.warn('Failed to send blocks to background:', err);
    }
}

function extractCleanContent() {
    const allowedTags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'a', 'strong', 'em', 'div', 'li', 'ul', 'ol', 'article', 'section', 'blockquote'];
    const blockedSelectors = ['header', 'footer', 'nav', 'aside', '.sidebar', '.menu', '.comments', '.share', '.subscribe'];

    function isVisibleAndAllowed(node) {
        const parent = node.parentElement;
        if (!parent) return false;

        const tag = parent.tagName.toLowerCase();
        if (!allowedTags.includes(tag)) return false;

        const style = window.getComputedStyle(parent);
        return style.display !== 'none' && style.visibility !== 'hidden' && /\S/.test(node.nodeValue);
    }

    function isInsideBlockedContainer(node) {
        let el = node.parentElement;
        while (el) {
            if (blockedSelectors.some(sel => el.matches(sel))) return true;
            el = el.parentElement;
        }
        return false;
    }

    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
        acceptNode: node => {
            if (!isVisibleAndAllowed(node)) return NodeFilter.FILTER_REJECT;
            if (isInsideBlockedContainer(node)) return NodeFilter.FILTER_REJECT;
            return NodeFilter.FILTER_ACCEPT;
        }
    });

    const textBlocks = [];
    while (walker.nextNode()) {
        textBlocks.push({
            text: walker.currentNode.nodeValue.trim(),
            tag: walker.currentNode.parentElement.tagName.toLowerCase()
        });
    }

    return textBlocks;
}
