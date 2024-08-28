# กล่องค้นหาเพื่อรับรหัสนายทหารนักเรียน
student_id = st.text_input("กรุณาใส่รหัสนายทหารนักเรียน:")

if "last_searched_id" not in st.session_state or st.session_state.last_searched_id != student_id:
    # เคลียร์ session_state เมื่อมีการใส่รหัสใหม่
    st.session_state.clear()
    st.session_state.last_searched_id = student_id

if student_id:
    # โหลดข้อมูลนายทหารนักเรียน
    df_students = pd.DataFrame(student_sheet.get_all_records())
    df_students['StudentID'] = df_students['StudentID'].astype(str).str.strip()

    # ค้นหาข้อมูลนายทหารนักเรียนด้วยรหัสนายทหารนักเรียน
    student_data = df_students[df_students['StudentID'] == student_id.strip()]

    if not student_data.empty:
        st.write("### ข้อมูลนายทหารนักเรียน")
        table_placeholder = st.empty()

        # เก็บค่าของฟิลด์ input ไว้ใน session state
        if "rank_name" not in st.session_state:
            st.session_state['rank_name'] = student_data.iloc[0]['RankName']
        if "branch" not in st.session_state:
            st.session_state['branch'] = student_data.iloc[0]['Branch']
        if "officer_type" not in st.session_state:
            st.session_state['officer_type'] = student_data.iloc[0]['OfficerType']
        if "other" not in st.session_state:
            st.session_state['other'] = student_data.iloc[0]['Other']
        if "rank" not in st.session_state:
            st.session_state['rank'] = str(student_data.iloc[0]['Rank'])
        if "position1" not in st.session_state:
            st.session_state['position1'] = str(student_data.iloc[0]['Position1'])
        if "position2" not in st.session_state:
            st.session_state['position2'] = str(student_data.iloc[0]['Position2'])
        if "position3" not in st.session_state:
            st.session_state['position3'] = str(student_data.iloc[0]['Position3'])

        # แสดงข้อมูลในตารางแนวตั้งรวมถึงตำแหน่งที่เลือก พร้อมดึงชื่อหน่วยจาก PositionDB
        table_placeholder.write(f"""
        <table>
            <tr><th>รหัสนักเรียน</th><td>{student_id}</td></tr>
            <tr><th>ยศ ชื่อ สกุล</th><td>{st.session_state['rank_name']}</td></tr>
            <tr><th>ลำดับ</th><td>{st.session_state['rank']}</td></tr>
            <tr><th>เหล่า</th><td>{st.session_state['branch']}</td></tr>
            <tr><th>กำเนิด</th><td>{st.session_state['officer_type']}</td></tr>
            <tr><th>อื่นๆ</th><td>{st.session_state['other']}</td></tr>
            <tr><th>ตำแหน่งลำดับ 1</th><td>{get_position_name(st.session_state['position1'])}</td></tr>
            <tr><th>ตำแหน่งลำดับ 2</th><td>{get_position_name(st.session_state['position2'])}</td></tr>
            <tr><th>ตำแหน่งลำดับ 3</th><td>{get_position_name(st.session_state['position3'])}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        # ส่วนที่เหลือของโค้ดสามารถคงเดิมได้
