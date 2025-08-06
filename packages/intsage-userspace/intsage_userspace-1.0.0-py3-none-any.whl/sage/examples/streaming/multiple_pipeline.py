import logging

from sage.api.local_environment import LocalEnvironment
from sage.lib.io_utils.sink import MemWriteSink, FileSink
from sage.lib.io_utils.source import FileSource

from sage.lib.rag.chunk import CharacterSplitter
from sage.lib.rag.generator import OpenAIGenerator
from sage.lib.rag.promptor import QAPromptor
from sage.lib.rag.retriever import DenseRetriever
from sage.lib.rag.writer import MemoryWriter

from sage.utils.config.loader import load_config

def ingest_pipeline_run():
    env = LocalEnvironment()
    # 构建数据处理流程
    source_stream = env.from_source(FileSource, config_for_ingest["source"])
    chunk_stream = source_stream.map(CharacterSplitter,config_for_ingest["chunk"])
    memwrite_stream= chunk_stream.map(MemoryWriter,config_for_ingest["writer"])
    sink_stream= memwrite_stream.sink(MemWriteSink,config_for_ingest["sink"])
    env.submit()
      # 启动管道

def qa_pipeline_run():
    """创建并运行数据处理管道"""
    env = LocalEnvironment()
    env.set_memory()
    # 构建数据处理流程
    query_stream = env.from_source(FileSource, config_for_qa["source"])
    query_and_chunks_stream = query_stream.map(DenseRetriever, config_for_qa["retriever"])
    prompt_stream = query_and_chunks_stream.map(QAPromptor, config_for_qa["promptor"])
    response_stream = prompt_stream.map(OpenAIGenerator, config_for_qa["generator"])
    response_stream.sink(FileSink, config_for_qa["sink"])
    # 提交管道并运行
    env.submit()
      # 启动管道

if __name__ == '__main__':
    # 加载配置并初始化日志
    config_for_ingest= load_config('../../resources/config/config_for_ingest.yaml')
    config_for_qa= load_config('../../resources/config/config_for_qa.yaml')
    logging.basicConfig(level=logging.INFO)
    ingest_pipeline_run()
    qa_pipeline_run()