import 'dart:math';
import 'dart:typed_data';

import 'package:photo_manager/photo_manager.dart';

/// Raised when the user did not grant photo-library access.
class PhotoPermissionDenied implements Exception {
  @override
  String toString() => 'Photo library permission was denied';
}

/// One sampled camera-roll photo: its library [id] (so a reshuffle can avoid
/// offering the same picture twice), a small [thumbnail] for the preview grid,
/// and the full-resolution [bytes] that get uploaded once confirmed.
class SampledPhoto {
  final String id;
  final Uint8List thumbnail;
  final Uint8List bytes;

  const SampledPhoto({
    required this.id,
    required this.thumbnail,
    required this.bytes,
  });
}

/// Size the preview thumbnails are requested at — the grid shows them a few
/// hundred logical pixels wide at most, so decoding the original is wasteful.
const _thumbnailSize = ThumbnailSize.square(300);

/// Samples random photos from the device camera roll using [PhotoManager],
/// which also owns the photo-library permission prompt (no separate
/// permission_handler dependency needed).
class PhotoSampler {
  final Random _random;

  PhotoSampler({Random? random}) : _random = random ?? Random();

  /// Requests photo-library permission, enumerates the most-recent album, and
  /// returns up to [count] randomly-sampled photos.
  ///
  /// Any asset whose id is in [exclude] is skipped, so a reshuffle offers
  /// pictures the player has already rejected as rarely as possible.
  ///
  /// Throws [PhotoPermissionDenied] if access is not granted.
  Future<List<SampledPhoto>> sampleRandomPhotos({
    required int count,
    Set<String> exclude = const {},
  }) async {
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

    final indices = _pickRandomIndices(total, count + exclude.length);
    final result = <SampledPhoto>[];
    for (final index in indices) {
      if (result.length == count) break;
      final page = await recent.getAssetListRange(start: index, end: index + 1);
      if (page.isEmpty) continue;
      final asset = page.first;
      if (exclude.contains(asset.id)) continue;
      final thumbnail = await asset.thumbnailDataWithSize(_thumbnailSize);
      final bytes = await asset.originBytes;
      if (thumbnail == null || bytes == null) continue;
      result.add(
        SampledPhoto(id: asset.id, thumbnail: thumbnail, bytes: bytes),
      );
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
