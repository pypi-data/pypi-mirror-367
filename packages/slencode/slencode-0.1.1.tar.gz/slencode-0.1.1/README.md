# SLEncode
Custom run-length encoding (RLE) algorithm for python implemented in Rust.

## Native Rust Binary
https://github.com/MetaAnomie/SLEncode/blob/main/releases/v0.1.0/SLEncode.exe<br><br>
<b>Usage:</b>
```
SLEncode.exe encode in.txt out.enc
SLEncode.exe decode out.enc orig.txt
```
## Python Usage

```python
import slencode

slencode.rle_encode_file("in.txt", "out.enc")
slencode.rle_decode_file("out.enc", "orig.txt")
```

## Performance

Benchmarked on a Dell XPS 8930, Core i7-9700 CPU @ 3.00GHz (8 core), 16 GB Ram<br>
Input Test File Size: 492 MB<br>

| Implementation | Operation | Duration |
| --- | --- | --- |
| Rust           | Encoding  | 23.01 Seconds | 
| Pure Python    | Encoding  | 65.97 Seconds | 

