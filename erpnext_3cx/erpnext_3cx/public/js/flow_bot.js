document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('boatman-ai-root')) return;

    const chatHtml = `
        <div id='boatman-ai-root' style='position: fixed; bottom: 30px; right: 30px; z-index: 10000; font-family: sans-serif;'>
            <div id='ai-window' style='display: none; width: 350px; height: 550px; background: white; border-radius: 30px 30px 30px 5px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); flex-direction: column; overflow: hidden; border: 1px solid #e6f3ff; margin-bottom: 20px;'>
                <div style='background: #1b7abf; color: white; padding: 15px 20px; display: flex; align-items: center; gap: 10px;'>
                    <div style='width: 8px; height: 8px; background: #48bb78; border-radius: 50%; box-shadow: 0 0 10px #48bb78;'></div>
                    <h3 style='margin: 0; font-size: 1.2rem; font-weight: 900; color: white !important;'>Flow Bot AI™</h3>
                    <button id='ai-close' style='margin-left: auto; background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer; line-height: 1;'>&times;</button>
                </div>
                <div id='ai-messages' style='flex: 1; padding: 20px; overflow-y: auto; background: #f8fafc; display: flex; flex-direction: column; gap: 15px;'>
                    <div style='align-self: flex-start; background: white; padding: 12px 16px; border-radius: 15px; border: 1px solid #e2e8f0; font-size: 0.95rem; line-height: 1.5;'>
                        Hello I am Flow Bot, an AI built for AAA Irrigation Service to help answer your questions and schedule your appointment. How can I help you today?
                    </div>
                </div>
                <div style='padding: 15px; background: white; border-top: 1px solid #edf2f7; display: flex; gap: 10px;'>
                    <input id='ai-input' type='text' placeholder='Ask a question...' style='flex: 1; padding: 10px 15px; border: 1px solid #e2e8f0; border-radius: 20px; outline: none; font-size: 0.95rem;'>
                    <button id='ai-send' style='background: #ea580c; color: white; border: none; padding: 8px 15px; border-radius: 20px; font-weight: 700; cursor: pointer;'>Send</button>
                </div>
                <div style='padding: 8px 10px; background: white; text-align: center; border-top: 1px solid #f1f5f9;'>
                    <div style='font-size: 0.5rem; font-style: italic; color: #94a3b8;'>Powered By Boatman Systems™</div>
                </div>
            </div>
            <button id='ai-trigger' style='background: linear-gradient(135deg, #1b7abf 0%, #059669 100%); color: white !important; border: none; padding: 12px 25px; border-radius: 50px; font-weight: 900; box-shadow: 0 10px 30px rgba(27, 122, 191, 0.4); cursor: pointer; display: flex; align-items: center; gap: 10px; transition: transform 0.3s;'>
                <span style='font-size: 1.2rem;'>🤖</span> <span style='font-size: 0.9rem; color: white !important;'>Flow Bot AI™</span>
            </button>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', chatHtml);

    const trigger = document.getElementById('ai-trigger');
    const window_div = document.getElementById('ai-window');
    const close = document.getElementById('ai-close');
    const send = document.getElementById('ai-send');
    const input = document.getElementById('ai-input');
    const messages = document.getElementById('ai-messages');

    trigger.onclick = () => { window_div.style.display = 'flex'; trigger.style.display = 'none'; };
    close.onclick = () => { window_div.style.display = 'none'; trigger.style.display = 'flex'; };

    const append = (text, type) => {
        const msg = document.createElement('div');
        msg.style.cssText = type === 'user' ? 'align-self: flex-end; background: #1b7abf; color: white; padding: 12px 16px; border-radius: 15px; font-size: 0.95rem; max-width: 85%;' : 'align-self: flex-start; background: white; padding: 12px 16px; border-radius: 15px; border: 1px solid #e2e8f0; font-size: 0.95rem; max-width: 85%; line-height: 1.5;';
        msg.innerHTML = text; messages.appendChild(msg); messages.scrollTop = messages.scrollHeight;
    };

    const handle = async () => {
        const text = input.value.trim(); if (!text) return;
        input.value = ''; append(text, 'user');
        const thinking = document.createElement('div'); 
        thinking.style.cssText = 'align-self: flex-start; background: #f1f5f9; padding: 8px 12px; border-radius: 10px; font-size: 0.8rem; color: #64748b;';
        thinking.innerText = 'Flow Bot is thinking...'; messages.appendChild(thinking);
        try {
            const res = await fetch('https://setup.aaairrigationservice.com/api/ai/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: text }) });
            const data = await res.json(); thinking.remove(); append(data.response || 'No response', 'ai');
        } catch (e) { thinking.remove(); append('Connection error.', 'ai'); }
    };

    send.onclick = handle;
    input.onkeypress = (e) => { if (e.key === 'Enter') handle(); };
});
