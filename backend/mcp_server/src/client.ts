// sample_project/src/client.ts
import fs from "node:fs";
import path from "node:path";
import FormData from "form-data";
import fetch from "node-fetch";
import { ParseImgResponse, DetectObjectResponse } from "./types";

type ParseImageArgs = {
  prompt: string;
  imagePath: string;  // local file to upload
};

type DetectObjectArgs = {
  file: string;
}

export class ParseImgClient {
  private PY_SERVER: string;

  constructor(baseUrl = "http://127.0.0.1:8080") {
    this.PY_SERVER = baseUrl;
  }

  async parseImage(args: ParseImageArgs): Promise<{ result: string }> {
    if (!args?.imagePath) throw new Error("imagePath is required");

    const url = `${this.PY_SERVER}/img/claude`;
    const filePath = path.resolve(args.imagePath);

    if (!fs.existsSync(filePath)) {
      throw new Error(`imagePath not found: ${filePath}`);
    }

    const form = new FormData();
    form.append("image", fs.createReadStream(filePath));

    const resp = await fetch(url, {
      method: "POST",
      body: form as any,
      headers: form.getHeaders() as any, // important for form-data package
    });

    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`POST /img/claude failed: ${resp.status} ${text}`);
    }

    const data = (await resp.json()) as ParseImgResponse;
    return { result: data?.text ?? "" };
  }

  async detectObject(args: DetectObjectArgs): Promise<{ result: string }> {
    if (!args?.file) throw new Error("imagePath is required");

    const url = `${this.PY_SERVER}/detect_objects`;
    const filePath = path.resolve(args.file);

    if (!fs.existsSync(filePath)) {
      throw new Error(`imagePath not found: ${filePath}`);
    }

    const form = new FormData();
    form.append("file", fs.createReadStream(filePath));

    const resp = await fetch(url, {
      method: "POST",
      body: form as any,
      headers: form.getHeaders() as any, // important for form-data package
    });

    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(`POST /detect_objects failed: ${resp.status} ${text}`);
    }

    const data = (await resp.json()) as DetectObjectResponse;
    return { result: data?.text ?? "" };
  }
}
