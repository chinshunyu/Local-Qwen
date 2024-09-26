from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import streamlit as st


with st.sidebar:
    st.markdown("## chat bot")
    max_length = st.slider("max_length", 0, 8192, 512, step=1)

st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot")


mode_name_or_path = '/data/cjy/qw/qw_model_file/qwen/Qwen2___5-7B-Instruct'

@st.cache_resource
def get_model():
    tokenizer = AutoTokenizer.from_pretrained(mode_name_or_path, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(mode_name_or_path, torch_dtype=torch.bfloat16,  device_map="auto")

    return tokenizer, model

tokenizer, model = get_model()

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "有什么可以帮您的？"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

    st.chat_message("user").write(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    input_ids = tokenizer.apply_chat_template(st.session_state.messages,tokenize=False,add_generation_prompt=True)
    model_inputs = tokenizer([input_ids], return_tensors="pt").to('cuda')
    generated_ids = model.generate(model_inputs.input_ids,max_new_tokens=max_length)
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

# streamlit run chat_bot.py --server.address 192.168.xxxxxx --server.port 6006
    