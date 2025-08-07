#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* sf.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscsf.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfcreate_ PETSCSFCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfcreate_ petscsfcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfreset_ PETSCSFRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfreset_ petscsfreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfsettype_ PETSCSFSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfsettype_ petscsfsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfgettype_ PETSCSFGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfgettype_ petscsfgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfdestroy_ PETSCSFDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfdestroy_ petscsfdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfsetup_ PETSCSFSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfsetup_ petscsfsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfsetfromoptions_ PETSCSFSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfsetfromoptions_ petscsfsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfsetrankorder_ PETSCSFSETRANKORDER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfsetrankorder_ petscsfsetrankorder
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfsetgraph_ PETSCSFSETGRAPH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfsetgraph_ petscsfsetgraph
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfsetgraphwithpattern_ PETSCSFSETGRAPHWITHPATTERN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfsetgraphwithpattern_ petscsfsetgraphwithpattern
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfcreateinversesf_ PETSCSFCREATEINVERSESF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfcreateinversesf_ petscsfcreateinversesf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfduplicate_ PETSCSFDUPLICATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfduplicate_ petscsfduplicate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfgetleafrange_ PETSCSFGETLEAFRANGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfgetleafrange_ petscsfgetleafrange
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfviewfromoptions_ PETSCSFVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfviewfromoptions_ petscsfviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfview_ PETSCSFVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfview_ petscsfview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfgetrankssf_ PETSCSFGETRANKSSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfgetrankssf_ petscsfgetrankssf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfgetmultisf_ PETSCSFGETMULTISF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfgetmultisf_ petscsfgetmultisf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfcompose_ PETSCSFCOMPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfcompose_ petscsfcompose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfcomposeinverse_ PETSCSFCOMPOSEINVERSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfcomposeinverse_ petscsfcomposeinverse
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfconcatenate_ PETSCSFCONCATENATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfconcatenate_ petscsfconcatenate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfregisterpersistent_ PETSCSFREGISTERPERSISTENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfregisterpersistent_ petscsfregisterpersistent
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfderegisterpersistent_ PETSCSFDEREGISTERPERSISTENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfderegisterpersistent_ petscsfderegisterpersistent
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscsfcreate_(MPI_Fint * comm,PetscSF *sf, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(sf);
 PetscBool sf_null = !*(void**) sf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFCreate(
	MPI_Comm_f2c(*(comm)),sf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sf_null && !*(void**) sf) * (void **) sf = (void *)-2;
}
PETSC_EXTERN void  petscsfreset_(PetscSF sf, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFReset(
	(PetscSF)PetscToPointer((sf) ));
}
PETSC_EXTERN void  petscsfsettype_(PetscSF sf,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(sf);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = PetscSFSetType(
	(PetscSF)PetscToPointer((sf) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  petscsfgettype_(PetscSF sf,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFGetType(
	(PetscSF)PetscToPointer((sf) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  petscsfdestroy_(PetscSF *sf, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(sf);
 PetscBool sf_null = !*(void**) sf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFDestroy(sf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sf_null && !*(void**) sf) * (void **) sf = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(sf);
 }
PETSC_EXTERN void  petscsfsetup_(PetscSF sf, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFSetUp(
	(PetscSF)PetscToPointer((sf) ));
}
PETSC_EXTERN void  petscsfsetfromoptions_(PetscSF sf, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFSetFromOptions(
	(PetscSF)PetscToPointer((sf) ));
}
PETSC_EXTERN void  petscsfsetrankorder_(PetscSF sf,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFSetRankOrder(
	(PetscSF)PetscToPointer((sf) ),*flg);
}
PETSC_EXTERN void  petscsfsetgraph_(PetscSF sf,PetscInt *nroots,PetscInt *nleaves,PetscInt *ilocal,PetscCopyMode *localmode,PetscSFNode *iremote,PetscCopyMode *remotemode, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
CHKFORTRANNULLINTEGER(ilocal);
*ierr = PetscSFSetGraph(
	(PetscSF)PetscToPointer((sf) ),*nroots,*nleaves,ilocal,*localmode,iremote,*remotemode);
}
PETSC_EXTERN void  petscsfsetgraphwithpattern_(PetscSF sf,PetscLayout map,PetscSFPattern *pattern, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
CHKFORTRANNULLOBJECT(map);
*ierr = PetscSFSetGraphWithPattern(
	(PetscSF)PetscToPointer((sf) ),
	(PetscLayout)PetscToPointer((map) ),*pattern);
}
PETSC_EXTERN void  petscsfcreateinversesf_(PetscSF sf,PetscSF *isf, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
PetscBool isf_null = !*(void**) isf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(isf);
*ierr = PetscSFCreateInverseSF(
	(PetscSF)PetscToPointer((sf) ),isf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! isf_null && !*(void**) isf) * (void **) isf = (void *)-2;
}
PETSC_EXTERN void  petscsfduplicate_(PetscSF sf,PetscSFDuplicateOption *opt,PetscSF *newsf, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
PetscBool newsf_null = !*(void**) newsf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newsf);
*ierr = PetscSFDuplicate(
	(PetscSF)PetscToPointer((sf) ),*opt,newsf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newsf_null && !*(void**) newsf) * (void **) newsf = (void *)-2;
}
PETSC_EXTERN void  petscsfgetleafrange_(PetscSF sf,PetscInt *minleaf,PetscInt *maxleaf, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
CHKFORTRANNULLINTEGER(minleaf);
CHKFORTRANNULLINTEGER(maxleaf);
*ierr = PetscSFGetLeafRange(
	(PetscSF)PetscToPointer((sf) ),minleaf,maxleaf);
}
PETSC_EXTERN void  petscsfviewfromoptions_(PetscSF A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscSFViewFromOptions(
	(PetscSF)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscsfview_(PetscSF sf,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscSFView(
	(PetscSF)PetscToPointer((sf) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscsfgetrankssf_(PetscSF sf,PetscSF *rsf, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
PetscBool rsf_null = !*(void**) rsf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(rsf);
*ierr = PetscSFGetRanksSF(
	(PetscSF)PetscToPointer((sf) ),rsf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! rsf_null && !*(void**) rsf) * (void **) rsf = (void *)-2;
}
PETSC_EXTERN void  petscsfgetmultisf_(PetscSF sf,PetscSF *multi, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
PetscBool multi_null = !*(void**) multi ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(multi);
*ierr = PetscSFGetMultiSF(
	(PetscSF)PetscToPointer((sf) ),multi);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! multi_null && !*(void**) multi) * (void **) multi = (void *)-2;
}
PETSC_EXTERN void  petscsfcompose_(PetscSF sfA,PetscSF sfB,PetscSF *sfBA, int *ierr)
{
CHKFORTRANNULLOBJECT(sfA);
CHKFORTRANNULLOBJECT(sfB);
PetscBool sfBA_null = !*(void**) sfBA ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sfBA);
*ierr = PetscSFCompose(
	(PetscSF)PetscToPointer((sfA) ),
	(PetscSF)PetscToPointer((sfB) ),sfBA);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sfBA_null && !*(void**) sfBA) * (void **) sfBA = (void *)-2;
}
PETSC_EXTERN void  petscsfcomposeinverse_(PetscSF sfA,PetscSF sfB,PetscSF *sfBA, int *ierr)
{
CHKFORTRANNULLOBJECT(sfA);
CHKFORTRANNULLOBJECT(sfB);
PetscBool sfBA_null = !*(void**) sfBA ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sfBA);
*ierr = PetscSFComposeInverse(
	(PetscSF)PetscToPointer((sfA) ),
	(PetscSF)PetscToPointer((sfB) ),sfBA);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sfBA_null && !*(void**) sfBA) * (void **) sfBA = (void *)-2;
}
PETSC_EXTERN void  petscsfconcatenate_(MPI_Fint * comm,PetscInt *nsfs,PetscSF sfs[],PetscSFConcatenateRootMode *rootMode,PetscInt leafOffsets[],PetscSF *newsf, int *ierr)
{
PetscBool sfs_null = !*(void**) sfs ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sfs);
CHKFORTRANNULLINTEGER(leafOffsets);
PetscBool newsf_null = !*(void**) newsf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newsf);
*ierr = PetscSFConcatenate(
	MPI_Comm_f2c(*(comm)),*nsfs,sfs,*rootMode,leafOffsets,newsf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sfs_null && !*(void**) sfs) * (void **) sfs = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newsf_null && !*(void**) newsf) * (void **) newsf = (void *)-2;
}
PETSC_EXTERN void  petscsfregisterpersistent_(PetscSF sf,MPI_Fint * unit, void*rootdata, void*leafdata, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFRegisterPersistent(
	(PetscSF)PetscToPointer((sf) ),
	MPI_Type_f2c(*(unit)),rootdata,leafdata);
}
PETSC_EXTERN void  petscsfderegisterpersistent_(PetscSF sf,MPI_Fint * unit, void*rootdata, void*leafdata, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFDeregisterPersistent(
	(PetscSF)PetscToPointer((sf) ),
	MPI_Type_f2c(*(unit)),rootdata,leafdata);
}
#if defined(__cplusplus)
}
#endif
