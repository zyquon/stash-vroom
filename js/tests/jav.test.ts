import { describe, it, expect } from 'vitest';
import { getJavInfo } from '../src/jav.js';

interface ExpectedResult {
  studio: string;
  mid: string;
  id: string;
  part: string;
}

type TestCase = [string, ExpectedResult | null];

describe('getJavInfo', () => {
  const testCases: TestCase[] = [
    // Non-JAV files (should return null)
    ['SkinRays_SunsetDance_180_LR.mp4', null],
    ['JillVR_1234.mp4', null],
    ['realhotvr-example-180_180x180_3dh_LR.mp4', null],
    ['reality-lovers-example-180_180x180_3dh_LR.mp4', null],
    ['sexbabesvr-example-180_180x180_3dh_LR.mp4', null],
    ['only3xvr-example-180_180x180_3dh_LR.mp4', null],
    ['wankzvr-example-180_180x180_3dh_LR.mp4', null],
    ['SLR-AsianSexVR-Title-1920p-48493-LR-180.mp4', null],
    ['[8K]Some.Person.TA.Directors.Cut.180.LR.mp4', null],

    // Depth Anything output files (should return null)
    ['tr 0123-4567-89fe-dcba Depth Anything div-5.0 con-0.0 fg-2.0 ipd-15._LRF.mp4', null],
    [
      'scene-25339.slider-.6 100d-3846-0b73-2af7 Portrait div-5.0 con-0.0 fg-1.0 ipd-8._LRF.mp4',
      null,
    ],

    // Standard JAV files
    ['CBIKMV-068.24399-SLR.mp4', { studio: 'CBIKMV', mid: '-', id: '068', part: '' }],
    ['dandyhqvr-011-b.MP4', { studio: 'DANDYHQVR', mid: '-', id: '011', part: 'B' }],
    ['DANDYHQVR 015 A.mp4', { studio: 'DANDYHQVR', mid: ' ', id: '015', part: 'A' }],
    ['pxvr00051.part1.mp4', { studio: 'PXVR', mid: '', id: '051', part: '1' }],
    ['ebvr00099-3.mp4', { studio: 'EBVR', mid: '', id: '099', part: '3' }],
    ['cafr333.mp4', { studio: 'CAFR', mid: '', id: '333', part: '' }],

    // SLR download format with JAV prefix
    [
      'TMAVR-200-1.SLR_TMAVR_Filename Part 1_2160p_47574_LR_180.mp4',
      { studio: 'TMAVR', mid: '-', id: '200', part: '1' },
    ],
    [
      'CAFR-219.SLR_CasanovA_Example Title_1920p_1234_LR_180.mp4',
      { studio: 'CAFR', mid: '-', id: '219', part: '' },
    ],

    // SIVR variants
    ['sivr00404vrv18khia1.mp4', { studio: 'SIVR', mid: '', id: '404', part: '1' }],
    ['sivr00410vrv18khia2.mp4', { studio: 'SIVR', mid: '', id: '410', part: '2' }],
    ['sivr00386_1_8k.mp4', { studio: 'SIVR', mid: '', id: '386', part: '1' }],
    ['sivr00378-3_8K.mp4', { studio: 'SIVR', mid: '', id: '378', part: '3' }],

    // WVR1 variants
    ['WVR-1001-2.mp4', { studio: 'WVR1', mid: '', id: '001', part: '2' }],
    ['WVR-100001.avi', { studio: 'WVR1', mid: '', id: '001', part: '' }],
    ['WVR-1-001.avi', { studio: 'WVR1', mid: '-', id: '001', part: '' }],
    ['WVR-10-001.avi', { studio: 'WVR1', mid: '-', id: '001', part: '' }],

    // WVR6 variants
    ['WVR6D-044_32360-SLR.mp4', { studio: 'WVR6', mid: '-', id: '044', part: '' }],
    ['wvr6d014.VR.mp4', { studio: 'WVR6', mid: '', id: '014', part: '' }],
    ['WVR6-D093.mp4', { studio: 'WVR6', mid: '-', id: '093', part: '' }],

    // WVR8 variants
    ['WVR8-006.mp4', { studio: 'WVR8', mid: '-', id: '006', part: '' }],
    ['wvr801A.VR.mp4', { studio: 'WVR8', mid: '', id: '001', part: 'A' }],
    ['WVR-08002-A.mp4', { studio: 'WVR8', mid: '', id: '002', part: 'A' }],
    ['WVR-8002-2.mp4', { studio: 'WVR8', mid: '', id: '002', part: '2' }],

    // WVR9 variants
    ['WVR-90009 Test VR3D_4K_LR_180.mp4', { studio: 'WVR9', mid: '', id: '009', part: '' }],
    ['wvr9c018A.VR.mp4', { studio: 'WVR9', mid: '', id: '018', part: 'A' }],
    ['wVr9d.078 VR Foo bar - baz 2048p_180_3dh.mp4', { studio: 'WVR9', mid: '.', id: '078', part: '' }],
  ];

  it.each(testCases)('parses "%s" correctly', (filename, expected) => {
    const result = getJavInfo(`/example/${filename}`);

    if (expected === null) {
      expect(result).toBeNull();
    } else {
      expect(result).not.toBeNull();
      expect(result!.studio).toBe(expected.studio);
      expect(result!.mid).toBe(expected.mid);
      expect(result!.id).toBe(expected.id);
      expect(result!.part).toBe(expected.part);
      expect(result!.filename).toBe(filename);
    }
  });

  it('throws on invalid input', () => {
    expect(() => getJavInfo('')).toThrow();
    // @ts-expect-error Testing invalid input
    expect(() => getJavInfo(null)).toThrow();
    // @ts-expect-error Testing invalid input
    expect(() => getJavInfo(undefined)).toThrow();
  });
});
