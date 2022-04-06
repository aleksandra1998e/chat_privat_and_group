import socket
import threading
import time


def receiving(name, sock) -> None:
    """
    Функция проверки поступающей информации

    :param name: Имя
    :param sock: Сокет
    :return:
    """
    while flag:
        try:
            while True:
                data, address = sock.recvfrom(1024)
                print(data.decode('utf-8'))
                time.sleep(1)
        except:
            pass


def chat_selection() -> None:
    """
    Функция выбора чата

    :return: None
    """
    while True:
        try:
            permission = input('Если вы хотите общаться в общем чате (ваши сообщения видят все '
                               'участники общего чата и вы получаете сообщения от всех участников общего чата) '
                               'отправьте в ответ 0. \n Если вы хотите общаться в личном чате отправьте в ответ 1.\n')
            if permission == '0':
                client.sendto(f'{name} permission=general_chat'.encode('utf-8'), server)
                print('Вы в общем чате.\n')
                break
            elif permission == '1':
                client.sendto(f'{name} permission=private_chat'.encode('utf-8'), server)
                print('Дождитесь других собеседников, готовых общаться в личном чате. \n')
                break
            print('Ошибка ввода. 0 - общий чат, 1 - личный чат.')
        except:
            client.sendto(f"[{name}] [left13579]".encode('utf-8'), server)
            break


host = socket.gethostbyname(socket.gethostname())
port = 0
server = ('127.0.1.1', 9090)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind((host, port))
client.setblocking(False)
join = False
flag = True


if __name__ == '__main__':
    name = input('Введите имя: ')
    for_clients = threading.Thread(target=receiving, args=("RecvThread", client))
    for_clients.start()

    if not join:
        client.sendto(f"{name} join to chat".encode('utf-8'), server)
        join = True

    chat_selection()

    while flag:
        try:
            message = input('')
            if message != '':
                client.sendto(f"[{name}]: {message}".encode('utf-8'), server)
            time.sleep(1)
        except:
            client.sendto(f"[{name}] [left13579]".encode('utf-8'), server)
            flag = False

    for_clients.join()
    client.close()
