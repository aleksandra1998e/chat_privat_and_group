import datetime
import logging.handlers
import socket
from typing import Tuple


def join_chat(address_by_client, data_by_client) -> None:
    """
    Функция приема нового клиента.
    В словарь clients записывается адрес клиента и имя

    :param address_by_client: адрес клиента
    :param data_by_client: данные от клиента
    :return: None
    """

    name = data_by_client.decode('utf-8').split()[:-3]
    clients[address_by_client] = name
    print(f'{datetime.datetime.now()}: {data_by_client.decode("utf-8")}. Address: {address_by_client[1]}')


def join_general_chat(address_by_client, data_by_client) -> None:
    """
    Функция присоединения к общему чату

    :param address_by_client: адрес клиента
    :param data_by_client: данные от клиента
    :return: None
    """

    general_chat.append(address_by_client)
    name = data_by_client.decode('utf-8').split()[:-1]
    for cl in general_chat:
        if cl != address_by_client:
            sock.sendto(f'{name} присоединился к общему чату.'.encode('utf-8'),
                        cl)
    print(f'{datetime.datetime.now()}: {name} [{address_by_client[1]}] '
          f'присоединился к общему чату.')


def join_private_chat(address_by_client) -> None:
    """
    Функция присоединения к личным чатам.

    :param address_by_client: адрес клиента
    :return: None
    """

    sock.sendto('Для общения введите адрес собеседника. \n '
                'К общению в личном чате готовы:'.encode('utf-8'), address_by_client)
    for cl in now_in_private:
        sock.sendto(f'{clients[cl]}. Адрес: {cl[1]}'.encode('utf-8'), address_by_client)
    if len(now_in_private) == 0:
        sock.sendto('0 человек'.encode('utf-8'), address_by_client)

    now_in_private.append(address_by_client)
    name = clients[address_by_client]
    for client_pr in now_in_private:
        if client_pr != address_by_client:
            sock.sendto(f'{name} готов к общению в личном чате. Aдрес: '
                        f'{address_by_client[1]}'.encode('utf-8'), client_pr)
    print(f'{datetime.datetime.now()}: {name} [{address_by_client[1]}] '
          f'выбрал общение в личном чате.')


def left_chat(data_by, address_by, some_chat) -> Tuple[bool, bytes]:
    """
    Функция сообщения о выходе участника из чата

    :param data_by: данные от клиента
    :param address_by: адрес клиента
    :param some_chat: чат из которого необходимо выйти
    :return: был ли удален пользователь (False - удален, True - нет)
    """

    if data_by.decode('utf-8').endswith('[left13579]'):
        data_by = f"[{data_by.decode('utf-8').split()[0][1:-1]}] " \
                         f"покинул чат.".encode('utf-8')
        some_chat.remove(address_by)
        clients.pop(address_by)
        return False, data_by
    else:
        return True, data_by


def message_general(address_by_client, data_by_client) -> None:
    """
    Функция обмена сообщениями в общем чате

    :param address_by_client: адрес клиента
    :param data_by_client: данные от клиента
    :return: None
    """

    count = 0
    flag, data_by_client = left_chat(data_by_client, address_by_client, general_chat)
    print(f"{datetime.datetime.now()} (в общем чате): {data_by_client.decode('utf-8')}")
    logger.info(f"{datetime.datetime.now()} (в общем чате): {data_by_client.decode('utf-8')}")
    for cl in general_chat:
        if cl != address_by_client:
            sock.sendto(data_by_client, cl)
            count += 1
    if count != 0 and flag:
        sock.sendto('Сообщение доставлено.'.encode('utf-8'), address)
    elif flag and count == 0:
        sock.sendto('Сообщение не доставлено.'.encode('utf-8'), address)


def new_private_chat(address_by_client, data_by_client) -> None:
    """
    Функция создания нового личного чата

    :param address_by_client: адрес клиента
    :param data_by_client: данные от клиента
    :return: None
    """

    num = data_by_client.decode('utf-8').split()[-1]
    fl = False
    if not num.isdigit():
        sock.sendto('Адрес должен состоять из цифр'.encode('utf-8'), address_by_client)
    else:
        for cl in now_in_private:
            if int(num) == cl[1]:
                num = cl
                private_chat[address_by_client] = num
                private_chat[num] = address_by_client
                now_in_private.remove(num)
                now_in_private.remove(address_by_client)
                fl = True
                sock.sendto(f'Начат личный чат с {clients[num]}'.encode('utf-8'), address_by_client)
                sock.sendto(f'Начат личный чат с {clients[address_by_client]}'.encode('utf-8'), num)
                break
        if fl:
            for cli in now_in_private:
                sock.sendto(f'{clients[num]} больше недоступен для личного чата'.encode('utf-8'), cli)
                sock.sendto(f'{clients[address_by_client]} больше недоступен для личного чата'.encode('utf-8'), cli)
        else:
            sock.sendto('Неизвестный адрес. Попробуйте еще.'.encode('utf-8'), address_by_client)


def message_private(address_by_client, data_by_client) -> None:
    """
    Функция обмена сообщениями в личном чате

    :param address_by_client:
    :param data_by_client:
    :return: None
    """

    if data_by_client.decode('utf-8').endswith('[left13579]'):
        data_by_client = f"[{data_by_client.decode('utf-8').split()[0][1:-1]}] покинул чат.".encode('utf-8')
        second = private_chat[address_by_client]
        private_chat.pop(second)
        clients.pop(address_by_client)
        sock.sendto(data_by_client, second)
        print(f"{datetime.datetime.now()}: {data_by_client.decode('utf-8')}")
    else:
        sock.sendto(data_by_client, private_chat[address_by_client])
        print(
            f"{datetime.datetime.now()}: В личном чате "
            f"{clients[address_by_client]}-{clients[private_chat[address_by_client]]} "
            f"{data_by_client.decode('utf-8')}"
        )
        logger.info(
            f"{datetime.datetime.now()}: В личном чате "
            f"{clients[address_by_client]}-{clients[private_chat[address_by_client]]} "
            f"{data_by_client.decode('utf-8')}"
        )
        sock.sendto('Сообщение доставлено.'.encode('utf-8'), address_by_client)


clients = {}
general_chat = []
now_in_private = []
private_chat = {}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.1.1', 9090))
logger = logging.getLogger('chat_logger')
logger.setLevel(logging.INFO)
handler = logging.handlers.SysLogHandler(address='/dev/log')
logger.addHandler(handler)


if __name__ == '__main__':
    print('Сервер включен')
    while True:
        try:
            data, address = sock.recvfrom(1024)
            if address not in clients:
                join_chat(address, data)
            elif data.decode('utf-8').endswith('permission=general_chat'):
                join_general_chat(address, data)
            elif data.decode('utf-8').endswith('permission=private_chat'):
                join_private_chat(address)
            else:
                if address in general_chat:
                    message_general(address, data)
                elif address in now_in_private:
                    flag_pr, data = left_chat(data, address, now_in_private)
                    if not flag_pr:
                        for client in now_in_private:
                            if client != address:
                                sock.sendto(f'{clients[address]} больше недоступен для личного чата.',
                                            client)
                        print(f"{datetime.datetime.now()}: {data.decode('utf-8')}")
                    else:
                        new_private_chat(address, data)

                elif address in private_chat.keys():
                    message_private(address, data)
                elif address in private_chat.values():
                    sock.sendto('Сообщение не доставлено.'.encode('utf-8'), address)

        except:
            print('\nСервер отключен')
            break
    sock.close()
