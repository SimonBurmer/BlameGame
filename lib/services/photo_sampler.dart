import 'dart:math';
import 'dart:typed_data';

import 'package:photo_manager/photo_manager.dart';

/// Raised when the user did not grant photo-library access.
class PhotoPermissionDenied implements Exception {
  @override
  String toString() => 'Photo library permission was denied';
}

/// Samples random photos from the device camera roll using [PhotoManager],
/// which also owns the photo-library permission prompt (no separate
/// permission_handler dependency needed).
class PhotoSampler {
  final Random _random;

  PhotoSampler({Random? random}) : _random = random ?? Random();

  /// Requests photo-library permission, enumerates the most-recent album, and
  /// returns the JPEG bytes of up to [count] randomly-sampled photos.
  ///
  /// Uses [AssetEntity.originBytes] to upload the full-resolution originals.
  /// (Swap for `thumbnailDataWithSize` if upload size/bandwidth becomes a
  /// concern — smaller payloads at the cost of image quality.)
  ///
  /// Throws [PhotoPermissionDenied] if access is not granted.
  Future<List<Uint8List>> sampleRandomPhotos({required int count}) async {
    final permission = await PhotoManager.requestPermissionExtend();
    if (!permission.isAuth && !permission.hasAccess) {
      throw PhotoPermissionDenied();
    }

    final albums = await PhotoManager.getAssetPathList(
      type: RequestType.image,
      onlyAll: true,
    );
    if (albums.isEmpty) return [];

    final recent = albums.first;
    final total = await recent.assetCountAsync;
    if (total == 0) return [];

    final indices = _pickRandomIndices(total, count);
    final result = <Uint8List>[];
    for (final index in indices) {
      final page = await recent.getAssetListRange(start: index, end: index + 1);
      if (page.isEmpty) continue;
      final bytes = await page.first.originBytes;
      if (bytes != null) result.add(bytes);
    }
    return result;
  }

  List<int> _pickRandomIndices(int total, int count) {
    final want = min(count, total);
    final chosen = <int>{};
    while (chosen.length < want) {
      chosen.add(_random.nextInt(total));
    }
    return chosen.toList();
  }
}
