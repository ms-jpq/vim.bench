import {
  CompletionItem,
  CompletionItemKind,
  InsertTextFormat,
  InsertTextMode,
  createConnection,
} from "vscode-languageserver/node";
import { argv, stdin, stdout } from "process";
import { deepEqual, ok } from "assert";

import { randomBytes } from "crypto";

const [, a_len, r_len, a_reps, r_reps] = argv;

deepEqual(a_len, "--word-len");
const word_len = parseInt(r_len);
ok(!isNaN(word_len));

deepEqual(a_reps, "--reps");
const reps = parseInt(r_reps);
ok(!isNaN(reps));

const conn = createConnection(stdin, stdout);

const gen = function* (): IterableIterator<CompletionItem> {
  for (let i = 0; i < reps; i++) {
    const rand = randomBytes(word_len).toString();
    yield {
      label: rand,
      kind: CompletionItemKind.Text,
      documentation: { kind: "markdown", value: rand },
      deprecated: false,
      preselect: false,
      sortText: rand,
      filterText: rand,
      insertText: rand,
      insertTextFormat: InsertTextFormat.PlainText,
      insertTextMode: InsertTextMode.asIs,
      command: { title: rand, command: rand },
      data: [rand, rand, rand, rand, rand, rand],
    };
  }
};

conn.onCompletion(() => ({ isIncomplete: true, items: [...gen()] }));
conn.listen();
