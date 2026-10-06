import Foundation
import Vision

// Private evidence review: report locations/pattern names, never recognized text.
let arguments = CommandLine.arguments
guard arguments.count == 3 else { fatalError("input manifest and new private output required") }
let inputURL = URL(fileURLWithPath: arguments[1])
let outputURL = URL(fileURLWithPath: arguments[2])
guard !FileManager.default.fileExists(atPath: outputURL.path) else { fatalError("refuse overwrite") }
let document = try JSONSerialization.jsonObject(with: Data(contentsOf: inputURL)) as! [[String: String]]
let patterns: [(String, String)] = [
    ("generated_one_time_password", "\\b[a-z2-9]{4}(?:-[a-z2-9]{4}){4}\\b"),
    ("jwt", "\\beyJ[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\b"),
    ("database_dsn", "postgres(?:ql)?://[^\\s]+"),
    ("private_key", "-----BEGIN(?: [A-Z]+)? PRIVATE KEY-----"),
    ("bearer", "(?i)\\bBearer\\s+[A-Za-z0-9._~+/-]{16,}=*")
]
let expressions = try patterns.map { (label, pattern) in (label, try NSRegularExpression(pattern: pattern)) }
var outputs: [[String: Any]] = []
for item in document {
    let path = item["path"]!
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["en-US"]
    request.usesLanguageCorrection = false
    request.usesCPUOnly = true
    let handler = VNImageRequestHandler(url: URL(fileURLWithPath: path), options: [:])
    do {
        try handler.perform([request])
        let lines = (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }
        let recognized = lines.joined(separator: "\n")
        let range = NSRange(recognized.startIndex..<recognized.endIndex, in: recognized)
        let findings = expressions.compactMap { label, expression in
            expression.firstMatch(in: recognized, range: range) == nil ? nil : label
        }
        outputs.append(["path": path, "image_sha256": item["sha256"]!, "recognized_line_count": lines.count, "credential_pattern_findings": findings, "recognition_status": "EXECUTED"])
    } catch {
        outputs.append(["path": path, "image_sha256": item["sha256"]!, "recognition_status": "FAILED", "error_type": String(describing: type(of: error))])
    }
}
let result: [String: Any] = ["scope": "Local macOS Vision accurate English OCR of synthetic browser captures; no recognized text is published. Pattern check only, not certification against arbitrary or unreadable secrets.", "image_count": outputs.count, "results": outputs]
let data = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
FileManager.default.createFile(atPath: outputURL.path, contents: data, attributes: [.posixPermissions: 0o600])
let flagged = outputs.filter { ($0["credential_pattern_findings"] as? [String] ?? []).count > 0 }.count
let failed = outputs.filter { ($0["recognition_status"] as? String) == "FAILED" }.count
print("images=\(outputs.count) flagged=\(flagged) recognition_failures=\(failed)")
