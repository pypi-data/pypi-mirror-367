import click
from pathlib import Path
import os
import sys
from tqdm import tqdm
import time
from dotenv import load_dotenv
import subprocess
import webbrowser

# 添加core目录到Python路径
current_dir = Path(__file__).resolve().parent
core_dir = current_dir.parent / "core"
sys.path.insert(0, str(core_dir))

# 现在可以导入core模块
from html_processor import HtmlProcessor
from dataset_processor import process_json_folder
from llm_predictor import process_predictions
from content_restorer import restore_text_from_json
from gpt_extaractor import process_all_html

# CLI主命令组
@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def cli_app():
    """
    Webis内容提取工具 - 从HTML文件中提取和清洗有价值的内容
    
    这个工具可以处理HTML文件，提取有价值的内容，过滤掉无关的噪声文本，
    并可以使用DeepSeek API进行额外的优化。
    
    使用示例:
    
      # 基本用法，处理input_folder中的HTML文件
      webis extract --input ./input_folder
      
      # 使用DeepSeek API进行优化
      webis extract --input ./input_folder --use-deepseek --api-key YOUR_API_KEY
      
      # 指定输出目录和标签概率文件
      webis extract --input ./input_folder --output ./results --tag-probs ./my_tags.json
    """
    pass

# 加载环境变量中的API密钥
def load_env_api_key():
    """从.env文件或环境变量中加载DeepSeek API密钥"""
    # 尝试加载.env文件（项目根目录）
    dotenv_path = Path(__file__).resolve().parent.parent.parent / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
    
    # 尝试获取API密钥
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if api_key and api_key != 'your_deepseek_api_key_here':
        return api_key
    return None

@cli_app.command('extract')
@click.option("--input", "-i", required=True, help="包含HTML文件的输入目录路径")
@click.option("--output", "-o", default="./output", help="处理结果的输出目录路径")
@click.option("--tag-probs", "-t", default=None, help="HTML标签概率配置文件的路径")
@click.option("--api-key", "-k", default=None, help="用于内容优化的DeepSeek API密钥（可选，默认从.env文件读取）")
@click.option("--use-deepseek", "-d", is_flag=True, help="是否使用DeepSeek API进行最终内容优化")
@click.option("--verbose", "-v", is_flag=True, help="显示详细的处理进度和信息")
def extract(input, output, tag_probs, api_key, use_deepseek, verbose):
    """从HTML文件中提取和清洗有价值的内容"""
    start_time = time.time()
    input_path = Path(input)
    output_path = Path(output)
    
    # 检查输入目录是否存在
    if not input_path.exists():
        click.secho(f"错误: 输入目录 '{input_path}' 不存在", fg='red')
        return
    
    # 检查是否有HTML文件
    html_files = list(input_path.glob("**/*.html"))
    if not html_files:
        click.secho(f"警告: 在输入目录中没有找到HTML文件", fg='yellow')
        return
    
    click.secho(f"找到 {len(html_files)} 个HTML文件", fg='green')
    
    # 如果没有指定tag_probs，则使用默认值
    if tag_probs is None:
        tag_probs = (Path(__file__).resolve().parent.parent.parent / 'config' / 'tag_probs.json')
        if verbose:
            click.echo(f"使用默认标签概率文件: {tag_probs}")
    
    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 数据预处理
    click.echo("步骤 1/4: HTML预处理...")
    processor = HtmlProcessor(input_path, output_path)
    processor.process_html_folder()
    
    # 数据集生成
    click.echo("步骤 2/4: 生成数据集...")
    dataset_output = output_path/"dataset"
    dataset_output.mkdir(parents=True, exist_ok=True)
    process_json_folder(
        output_path/"content_output",
        dataset_output/"extra_datasets.json",
        tag_probs
    )
    
    # 模型预测
    click.echo("步骤 3/4: 执行模型预测...")
    process_predictions(
        dataset_output/"extra_datasets.json",
        dataset_output/"pred_results.json"
    )
    
    # 结果恢复
    click.echo("步骤 4/4: 恢复处理文本...")
    predicted_texts_dir = output_path/"predicted_texts"
    predicted_texts_dir.mkdir(parents=True, exist_ok=True)
    restore_text_from_json(
        dataset_output/"pred_results.json",
        predicted_texts_dir
    )
    click.secho(f"节点及局部处理处理完成! 结果保存在: {predicted_texts_dir}", fg='green')
    
    # DeepSeek提取（如果启用）
    if use_deepseek:
        # 如果命令行未提供API密钥，尝试从环境变量获取
        if api_key is None:
            api_key = load_env_api_key()
            if api_key and verbose:
                click.secho(f"使用环境变量中的DeepSeek API密钥", fg='blue')
        
        # 检查最终是否有有效的API密钥
        if api_key is None:
            click.secho("错误: 使用DeepSeek提取功能需要提供API密钥", fg='red')
            click.echo("可以通过以下方式提供API密钥:")
            click.echo("1. 使用命令行参数 --api-key")
            click.echo("2. 在.env文件中设置 DEEPSEEK_API_KEY")
            click.echo("3. 设置环境变量 DEEPSEEK_API_KEY")
            return
            
        click.secho("正在进行大模型清洗...", fg='blue')
        deepseek_output_path = output_path/"deepseek_predicted_texts"
        deepseek_output_path.mkdir(parents=True, exist_ok=True)
        
        with tqdm(total=len(html_files), desc="优化文件") as pbar:
            def progress_callback(completed, total):
                pbar.update(1)
                
            process_all_html(input_path, deepseek_output_path, api_key)
            
        click.secho(f"DeepSeek优化完成! 结果保存在: {deepseek_output_path}", fg='green')
    
    # 显示处理统计信息
    elapsed_time = time.time() - start_time
    click.echo(f"\n处理统计:")
    click.echo(f"- 处理的HTML文件数量: {len(html_files)}")
    click.echo(f"- 总处理时间: {elapsed_time:.2f} 秒")
    if use_deepseek:
        deepseek_files = list(deepseek_output_path.glob("*.txt"))
        click.echo(f"- DeepSeek优化后的文件数量: {len(deepseek_files)}")
    
    click.secho("\n处理完成!", fg='green', bold=True)

# 添加其他实用命令

@cli_app.command('version')
def version():
    """显示版本信息"""
    click.echo("Webis内容提取工具 v1.0.0")
    click.echo("© 2025 Webis团队")

@cli_app.command('check-api')
@click.option("--api-key", "-k", required=True, help="DeepSeek API密钥")
def check_api(api_key):
    """测试DeepSeek API连接状态"""
    click.echo("正在检查DeepSeek API连接...")
    try:
        # 导入requests以检查连接
        import requests
        
        url = "https://api.siliconflow.cn/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 发送一个简单请求测试API
        data = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "max_tokens": 5
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            click.secho("✓ API连接正常!", fg='green')
        else:
            click.secho(f"× API连接失败: 状态码 {response.status_code}", fg='red')
            click.echo(f"响应: {response.text}")
    
    except Exception as e:
        click.secho(f"× API连接错误: {str(e)}", fg='red')

@cli_app.command('gui')
def gui():
    """启动Webis前端可视化界面 (Vue3)"""
    frontend_dir = Path(__file__).resolve().parent.parent.parent / 'frontend'

    # 检查前端目录是否存在
    if not frontend_dir.exists():
        click.secho(f"错误: 前端目录不存在: {frontend_dir}", fg='red')
        return

    # 检查package.json是否存在
    package_json = frontend_dir / 'package.json'
    if not package_json.exists():
        click.secho(f"错误: package.json不存在: {package_json}", fg='red')
        return

    # 检查npm是否已安装
    try:
        subprocess.run(['npm', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.secho("错误: npm未安装，请先安装Node.js和npm", fg='red')
        return

    # 检查node_modules是否存在，如果不存在则安装依赖
    node_modules = frontend_dir / 'node_modules'
    if not node_modules.exists():
        click.echo("正在安装前端依赖...")
        try:
            subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
            click.secho("✓ 依赖安装完成", fg='green')
        except subprocess.CalledProcessError as e:
            click.secho(f"错误: 依赖安装失败: {e}", fg='red')
            return

    # 启动vite开发服务器
    try:
        # 优先尝试本地node_modules/.bin/vite
        vite_path = frontend_dir / 'node_modules' / '.bin' / 'vite'
        if vite_path.exists():
            cmd = [str(vite_path)]
        else:
            cmd = ['npx', 'vite']
        
        # 检查端口是否被占用
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_in_use = False
        try:
            sock.bind(('localhost', 5173))
            sock.close()
        except socket.error:
            port_in_use = True
            
        if port_in_use:
            click.secho("警告: 端口5173已被占用，请确保没有其他Vite服务正在运行", fg='yellow')
            return

        click.echo('正在启动前端开发服务器...')
        server = subprocess.Popen(cmd, cwd=frontend_dir)
        
        # 等待服务器启动，最多等待10秒
        max_attempts = 20
        for i in range(max_attempts):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if sock.connect_ex(('localhost', 5173)) == 0:
                    break
                sock.close()
                time.sleep(0.5)
            except socket.error:
                pass
            
        url = 'http://localhost:5173/'
        click.echo(f'正在打开浏览器: {url}')
        webbrowser.open(url)
        
        # 优雅地处理Ctrl+C
        try:
            server.wait()
        except KeyboardInterrupt:
            click.echo('\n正在关闭服务器...')
            server.terminate()
            server.wait()
            click.echo('服务器已关闭')
    except Exception as e:
        click.secho(f'启动前端失败: {e}', fg='red')
        if 'server' in locals():
            server.terminate()
            server.wait()

if __name__ == "__main__":
    cli_app()