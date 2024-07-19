from http import HTTPStatus
from dashscope import Application


class QwenBaiLian:
    def __init__(self, app_id) -> None:
        self.app_id = app_id

    def chat(self, question):
        responses = Application.call(app_id=self.app_id,
                                     prompt=question,
                                     stream=True,
                                     incremental_output=True
                                     )
        return responses

def call_with_stream():
    llm = QwenBaiLian(api_key='a**')
    answer = llm.chat(question="19*2+8/2等于多少")
    for response in answer:
        if response.status_code != HTTPStatus.OK:
            print('request_id=%s, code=%s, message=%s\n' % (
                response.request_id, response.status_code, response.message))
        else:
            print('response=%s\n' % (response))

if __name__ == '__main__':
    call_with_stream()
