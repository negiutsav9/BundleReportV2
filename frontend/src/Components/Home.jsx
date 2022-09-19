import React from 'react';
import {useState} from 'react'
import './Home.css'
import { useNavigate } from 'react-router-dom';
import Papa from 'papaparse'


function Home(props) {

    const navigate = useNavigate()

    //states for loading screen processing
    const [loading, setLoading] = useState(false)

    //states for form information
    const [title, setTitle] = useState("")
    const [isMigr, setisMigr] = useState('off')
    const [isSQL, setisSQL] = useState('off')
    const [fileMigr, setfileMigr] = useState(undefined)
    const [fileSQL, setfileSQL] = useState(undefined)
    const [inclOrg, setinclOrg] = useState('off')
    const [startDate, setStartDate] = useState(undefined)
    const [endDate, setEndDate] = useState(undefined)
    const [issue, setIssue] = useState("")
    const runningYear = '2022-23'
    /*
    useEffect(() => {
        // declare the async data fetching function
        const fetchData = async () => {
            // get the data from the api
            const response = await fetch('http://localhost:5000/status');
            // convert the data to json
            const json = await response.json();
            setCount(json['count'])
            setTotalCount(json['total'])
            setCurrent(json['current'])
        }
      
        // call the function
        fetchData()
          // make sure to catch any error
          .catch(console.error);
      })*/

    //function to handle the submission and send the form response to flask server
    let handleSubmit = async (event) => {
        
        event.preventDefault();
        setLoading(true);
        console.log(title)
        console.log(isMigr)
        console.log(isSQL)
        console.log(fileMigr)
        console.log(fileSQL)
        console.log(inclOrg)
        console.log(startDate)
        console.log(endDate)
        console.log(issue)

        const form = {
            title:title,
            isMigr:isMigr,
            isSQL:isSQL,
            fileMigr:fileMigr,
            fileSQL:fileSQL,
            inclOrg:inclOrg,
            startDate:startDate,
            endDate:endDate,
            issue:issue
        }

        await fetch("http://localhost:5000/form",{
            method:'post',
            credentials:"include",
            headers:{
                'Accept':'application/json, text/plain',
                'Content-Type':'application/json'
            },
            mode:'cors',
            body:JSON.stringify(form)
        })
        .then((res)=>console.log(res))
        .catch(console.error)

        setLoading(false)
        navigate("/dashboard",{state:{id:1, name:title}});
        
    }

    const handleMigrUpload = (e) => {
         Papa.parse(e.target.files[0], {
            header:false,
            skipEmptyLines:true,
            complete: (result) => {setfileMigr(result)}
         })
    };

    const handleSQLUpload = (e) => {
        Papa.parse(e.target.files[0], {
           header:false,
           skipEmptyLines:true,
           complete: (result) => {setfileSQL(result)}
        })
   };
      
    if(loading){
        return(
            <div className='load-page'>
                <div className='Title'>
                    Bundle Report Generator
                </div>
                <div className="loader"></div>
            </div>
        )
    } else {
        return ( 
            <div className='Home-Page'>
                <div className='Title'>
                    Bundle Report Generator
                </div>
                <div className='Form-Div'>
                    <form method="POST" encType="multipart/form-data" action='' onSubmit={handleSubmit}>
                        <label>Title </label>
                        <input 
                            name='title' 
                            className='title-input' 
                            type='text' 
                            value={title}
                            size="45"
                            placeholder='Bundle Report' 
                            onChange = {(e)=>setTitle(e.target.value)} 
                        />
                        <br/>
                        <label>JIRA </label>
                        <input 
                            name='issue' 
                            className='issue-input' 
                            type='text' 
                            value={issue}
                            size="45"
                            placeholder='HRS-####' 
                            onChange = {(e)=>setIssue(e.target.value)} 
                        />
                        <br/>
                        <input name='incl_migr' 
                            type='checkbox' 
                            onChange={(e)=>setisMigr(e.target.value)}
                        /> 
                        <label>Include Migrated Bundle</label>
                        <br/>
                        <span className='tab'></span>
                        <input name='incl_sql' 
                            type='checkbox' 
                            onChange={(e)=>setisSQL(e.target.value)}
                        /> 
                        <label>Include SQL Updates</label>
                        <br/>
                        <label>Upload Migration Query Result </label>
                        <br/>
                        <input name='file_migr' type="file" className='migr-upload' accept='.csv' onChange = {handleMigrUpload}/>
                        <br/>
                        <label>Upload SQL Query Result </label>
                        <br/>
                        <input name='file_sql' type="file" className='sql-upload' accept='.csv' onChange = {handleSQLUpload}/>
                        <br/>
                        <input name='incl_org' 
                            type='checkbox' 
                            onChange={(e)=>setinclOrg(e.target.value)}
                        />
                        <label>Include Organization Department Update</label>
                        <br/>
                        <label>Start Date </label>
                        <input name='start_date' type='date' value={startDate} className='start-date' onChange={(e)=>setStartDate(e.target.value)}/>
                        <br/>
                        <label>End Date </label>
                        <input name='end_date' type='date' value={endDate} className='end-date' onChange={(e)=>setEndDate(e.target.value)}/>
                        <br/>
                        <input className="submit-button" type="submit" value="Submit"/>     
                    </form>
                </div>
                <div className='version'>
                    Version {runningYear}
                </div> 
            </div>
        );
    }
}

export default Home;