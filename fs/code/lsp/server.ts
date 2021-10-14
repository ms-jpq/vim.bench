import {
  CompletionItem,
  CompletionItemKind,
  InsertTextFormat,
  InsertTextMode,
  createConnection,
} from "vscode-languageserver/node.js";
import { env, stdin, stdout } from "process";
import { notEqual, ok } from "assert";

import { readFile } from "fs/promises";
import { setTimeout } from "timers/promises";

const gen = ({
  use_cache,
  pool,
}: Readonly<{
  use_cache: boolean;
  pool: readonly { delay: number; words: readonly string[] }[];
}>) => {
  const conn = createConnection(stdin, stdout);

  const gen = (async function* (): AsyncIterableIterator<
    IterableIterator<CompletionItem>
  > {
    while (true) {
      for (const { delay, words } of pool) {
        await setTimeout(delay);
        yield (function* () {
          for (const word of words) {
            const item: CompletionItem = {
              label: word,
              kind: CompletionItemKind.Text,
              documentation: { kind: "markdown", value: word },
              deprecated: false,
              preselect: false,
              sortText: word,
              filterText: word,
              insertText: word,
              insertTextFormat: InsertTextFormat.PlainText,
              insertTextMode: InsertTextMode.asIs,
              command: { title: word, command: word },
              data: [word, word, word, word, word, word],
            };
            yield item;
          }
        })();
      }
    }
  })();

  conn.onInitialize(() => ({
    capabilities: {
      completionProvider: {},
    },
  }));
  conn.onCompletion(async () => ({
    isIncomplete: !use_cache,
    items: [...(await gen.next()).value],
  }));
  conn.listen();
};

const cache = parseInt(env.TST_LSP_CACHE ?? "");
notEqual(cache, NaN);
const use_cache = Boolean(cache);
const pool_path = env.TST_LSP_INPUT;
ok(pool_path);

const json = await readFile(pool_path, { encoding: "utf-8" });
const pool = JSON.parse(json);
gen({ use_cache, pool });
