import stash_vroom.jav as jav

def test_get_jav_info():
    tests = (
        ('SkinRays_SunsetDance_180_LR.mp4'             , None                                 ),
        ('JillVR_1234.mp4'                             , None                                 ),
        ('CBIKMV-068.24399-SLR.mp4'                    , ('CBIKMV'   , '-' , '068'   , ''    )),
        ('dandyhqvr-011-b.MP4'                         , ('DANDYHQVR', '-' , '011'   , 'B'   )),
        ('DANDYHQVR 015 A.mp4'                         , ('DANDYHQVR', ' ' , '015'   , 'A'   )),
        ('pxvr00051.part1.mp4'                         , ('PXVR'     , ''  , '051'   , '1'   )),
        ('ebvr00099-3.mp4'                             , ('EBVR'     , ''  , '099'   , '3'   )),
        ('cafr333.mp4'                                 , ('CAFR'     , ''  , '333'   , ''    )),
        ('realhotvr-example-180_180x180_3dh_LR.mp4'    , None),
        ('reality-lovers-example-180_180x180_3dh_LR.mp4',None),
        ('sexbabesvr-example-180_180x180_3dh_LR.mp4'   , None),
        ('only3xvr-example-180_180x180_3dh_LR.mp4'     , None),
        ('wankzvr-example-180_180x180_3dh_LR.mp4'      , None),
        ('SLR-AsianSexVR-Title-1920p-48493-LR-180.mp4' , None),
        ('TMAVR-200-1.SLR_TMAVR_Filename Part 1_2160p_47574_LR_180.mp4', ('TMAVR', '-', '200', '1')),
        ('CAFR-219.SLR_CasanovA_Example Title_1920p_1234_LR_180.mp4'   , ('CAFR' , '-', '219', '' )),

        ('sivr00404vrv18khia1.mp4'                     , ('SIVR'     , ''  , '404'   , '1'   )),
        ('sivr00410vrv18khia2.mp4'                     , ('SIVR'     , ''  , '410'   , '2'   )),
        ('sivr00386_1_8k.mp4'                          , ('SIVR'     , ''  , '386'   , '1'   )),
        ('sivr00378-3_8K.mp4'                          , ('SIVR'     , ''  , '378'   , '3'   )),
        ('WVR-1001-2.mp4'                              , ('WVR1'     , ''  , '001'   , '2'   )),
        ('WVR-100001.avi'                              , ('WVR1'     , ''  , '001'   , ''    )),
        ('WVR-1-001.avi'                               , ('WVR1'     , '-' , '001'   , ''    )),
        ('WVR-10-001.avi'                              , ('WVR1'     , '-' , '001'   , ''    )),
        ('WVR6D-044_32360-SLR.mp4'                     , ('WVR6'     , '-' , '044'   , ''    )),
        ('wvr6d014.VR.mp4'                             , ('WVR6'     , ''  , '014'   , ''    )),
        ('WVR6-D093.mp4'                               , ('WVR6'     , '-' , '093'   , ''    )),
        ('WVR8-006.mp4'                                , ('WVR8'     , '-' , '006'   , ''    )),
        ('wvr801A.VR.mp4'                              , ('WVR8'     , ''  , '001'   , 'A'   )),
        ('WVR-08002-A.mp4'                             , ('WVR8'     , ''  , '002'   , 'A'   )),
        ('WVR-8002-2.mp4'                              , ('WVR8'     , ''  , '002'   , '2'   )),
        ('WVR-90009 Test VR3D_4K_LR_180.mp4'           , ('WVR9'     , ''  , '009'   , ''    )),
        ('wvr9c018A.VR.mp4'                            , ('WVR9'     , ''  , '018'   , 'A'   )),
        ('wVr9d.078 VR Foo bar - baz 2048p_180_3dh.mp4', ('WVR9'     , '.' , '078'   , ''    )),
    )

    for test in tests:
        filename, expected = test
        e_studio, e_mid, e_id, e_part = expected if expected else (None, None, None, None)

        jav_info = jav.get_jav_info(f'/example/{filename}')

        if not jav_info and expected is None:
            continue
        elif jav_info and expected is None:
            raise Exception(f'Expected None for {filename}, but got: {jav_info}')
        elif not jav_info and expected:
            raise Exception(f'Got None for {filename}, but expected: {expected}')
        else: # both jav and expected
            r_studio, r_mid, r_id, r_part = None, None, None, None

            if jav_info['studio'] != e_studio:
                r_studio = repr(jav_info['studio']) + ' vs ' + repr(e_studio)

            if jav_info['mid'] != e_mid:
                r_mid = repr(jav_info['mid']) + ' vs ' + repr(e_mid)

            if jav_info['id'] != e_id:
                r_id = repr(jav_info['id']) + ' vs ' + repr(e_id)

            if jav_info['part'] != e_part:
                r_part = repr(jav_info['part']) + ' vs ' + repr(e_part)

            if r_studio or r_mid or r_id or r_part:
                raise Exception(f'For {filename}:\n'
                                f'  Studio: {r_studio}\n'
                                f'  MID   : {r_mid}\n'
                                f'  ID    : {r_id}\n'
                                f'  Part  : {r_part}\n'
                                f'Got: {jav_info}')