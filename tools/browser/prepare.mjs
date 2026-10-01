// Extract the packaged Linux browser without requiring chown or external browser downloads.
import fs from "node:fs/promises";
import path from "node:path";
import { brotliDecompressSync } from "node:zlib";
import { execFileSync } from "node:child_process";
const out = path.resolve(".local/browser");
await fs.mkdir(out, { recursive: true });
const bin = path.resolve("tools/browser/node_modules/@sparticuz/chromium/bin");
for (const name of ["chromium", "al2023.tar", "fonts.tar", "swiftshader.tar"]) {
  const data = brotliDecompressSync(
    await fs.readFile(path.join(bin, name + ".br")),
  );
  const dest = path.join(out, name);
  await fs.writeFile(dest, data);
  if (name.endsWith(".tar"))
    execFileSync(process.env.PYTHON || "python3", [
      "-c",
      "import sys,tarfile;tarfile.open(sys.argv[1]).extractall(sys.argv[2],filter='data')",
      dest,
      out,
    ]);
  else await fs.chmod(dest, 0o755);
}
await fs.mkdir(path.join(out, "font-cache"), { recursive: true });
await fs.writeFile(
  path.join(out, "fonts.conf"),
  `<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig><dir>/usr/share/fonts</dir><dir>${out}/fonts</dir><cachedir>${out}/font-cache</cachedir><alias><family>system-ui</family><prefer><family>Open Sans</family></prefer></alias><alias><family>sans-serif</family><prefer><family>Open Sans</family></prefer></alias></fontconfig>`,
);
console.log("Browser prepared.");
