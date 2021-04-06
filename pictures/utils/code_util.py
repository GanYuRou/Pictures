# -*- encoding: utf-8 -*-

import time


class CodeUtil:

    __alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    @staticmethod
    def gen_code(prefix):
        now_ts = int(time.time() * 1000)
        return prefix + CodeUtil.hash_id(now_ts)

    @staticmethod
    def hash_id(num):
        hash_list = []
        alphabet_len = len(CodeUtil.__alphabet)

        while num > 0:
            index = int(num % alphabet_len)

            if 0 <= index < alphabet_len:
                hash_list.append(CodeUtil.__alphabet[index])

            num //= alphabet_len

        return ''.join(hash_list)


if __name__ == '__main__':
    hash_id = CodeUtil.gen_code('UC')
