#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dmlabel.c */
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

#include "petscdmlabel.h"
#include "petscsection.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelcreate_ DMLABELCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelcreate_ dmlabelcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelsetup_ DMLABELSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelsetup_ dmlabelsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabeladdstratum_ DMLABELADDSTRATUM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabeladdstratum_ dmlabeladdstratum
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabeladdstrata_ DMLABELADDSTRATA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabeladdstrata_ dmlabeladdstrata
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabeladdstratais_ DMLABELADDSTRATAIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabeladdstratais_ dmlabeladdstratais
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelview_ DMLABELVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelview_ dmlabelview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelreset_ DMLABELRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelreset_ dmlabelreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabeldestroy_ DMLABELDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabeldestroy_ dmlabeldestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelduplicate_ DMLABELDUPLICATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelduplicate_ dmlabelduplicate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelcomputeindex_ DMLABELCOMPUTEINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelcomputeindex_ dmlabelcomputeindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelcreateindex_ DMLABELCREATEINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelcreateindex_ dmlabelcreateindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabeldestroyindex_ DMLABELDESTROYINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabeldestroyindex_ dmlabeldestroyindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgetbounds_ DMLABELGETBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgetbounds_ dmlabelgetbounds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelhasvalue_ DMLABELHASVALUE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelhasvalue_ dmlabelhasvalue
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelhaspoint_ DMLABELHASPOINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelhaspoint_ dmlabelhaspoint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelstratumhaspoint_ DMLABELSTRATUMHASPOINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelstratumhaspoint_ dmlabelstratumhaspoint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgetdefaultvalue_ DMLABELGETDEFAULTVALUE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgetdefaultvalue_ dmlabelgetdefaultvalue
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelsetdefaultvalue_ DMLABELSETDEFAULTVALUE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelsetdefaultvalue_ dmlabelsetdefaultvalue
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgetvalue_ DMLABELGETVALUE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgetvalue_ dmlabelgetvalue
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelsetvalue_ DMLABELSETVALUE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelsetvalue_ dmlabelsetvalue
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelclearvalue_ DMLABELCLEARVALUE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelclearvalue_ dmlabelclearvalue
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelinsertis_ DMLABELINSERTIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelinsertis_ dmlabelinsertis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgetnumvalues_ DMLABELGETNUMVALUES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgetnumvalues_ dmlabelgetnumvalues
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgetvalueis_ DMLABELGETVALUEIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgetvalueis_ dmlabelgetvalueis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgetvaluebounds_ DMLABELGETVALUEBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgetvaluebounds_ dmlabelgetvaluebounds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgetnonemptystratumvaluesis_ DMLABELGETNONEMPTYSTRATUMVALUESIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgetnonemptystratumvaluesis_ dmlabelgetnonemptystratumvaluesis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgetvalueindex_ DMLABELGETVALUEINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgetvalueindex_ dmlabelgetvalueindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelhasstratum_ DMLABELHASSTRATUM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelhasstratum_ dmlabelhasstratum
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgetstratumsize_ DMLABELGETSTRATUMSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgetstratumsize_ dmlabelgetstratumsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgetstratumbounds_ DMLABELGETSTRATUMBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgetstratumbounds_ dmlabelgetstratumbounds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgetstratumis_ DMLABELGETSTRATUMIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgetstratumis_ dmlabelgetstratumis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelsetstratumis_ DMLABELSETSTRATUMIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelsetstratumis_ dmlabelsetstratumis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelclearstratum_ DMLABELCLEARSTRATUM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelclearstratum_ dmlabelclearstratum
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelsetstratumbounds_ DMLABELSETSTRATUMBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelsetstratumbounds_ dmlabelsetstratumbounds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgetstratumpointindex_ DMLABELGETSTRATUMPOINTINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgetstratumpointindex_ dmlabelgetstratumpointindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelfilter_ DMLABELFILTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelfilter_ dmlabelfilter
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelpermute_ DMLABELPERMUTE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelpermute_ dmlabelpermute
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabeldistribute_ DMLABELDISTRIBUTE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabeldistribute_ dmlabeldistribute
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgather_ DMLABELGATHER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgather_ dmlabelgather
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelpropagatebegin_ DMLABELPROPAGATEBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelpropagatebegin_ dmlabelpropagatebegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelpropagateend_ DMLABELPROPAGATEEND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelpropagateend_ dmlabelpropagateend
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelconverttosection_ DMLABELCONVERTTOSECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelconverttosection_ dmlabelconverttosection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelsettype_ DMLABELSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelsettype_ dmlabelsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlabelgettype_ DMLABELGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlabelgettype_ dmlabelgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsectioncreateglobalsectionlabel_ PETSCSECTIONCREATEGLOBALSECTIONLABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsectioncreateglobalsectionlabel_ petscsectioncreateglobalsectionlabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsectionsymlabelsetlabel_ PETSCSECTIONSYMLABELSETLABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsectionsymlabelsetlabel_ petscsectionsymlabelsetlabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsectionsymcreatelabel_ PETSCSECTIONSYMCREATELABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsectionsymcreatelabel_ petscsectionsymcreatelabel
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmlabelcreate_(MPI_Fint * comm, char name[],DMLabel *label, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool label_null = !*(void**) label ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(label);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMLabelCreate(
	MPI_Comm_f2c(*(comm)),_cltmp0,label);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! label_null && !*(void**) label) * (void **) label = (void *)-2;
}
PETSC_EXTERN void  dmlabelsetup_(DMLabel label, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelSetUp(
	(DMLabel)PetscToPointer((label) ));
}
PETSC_EXTERN void  dmlabeladdstratum_(DMLabel label,PetscInt *value, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelAddStratum(
	(DMLabel)PetscToPointer((label) ),*value);
}
PETSC_EXTERN void  dmlabeladdstrata_(DMLabel label,PetscInt *numStrata, PetscInt stratumValues[], int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLINTEGER(stratumValues);
*ierr = DMLabelAddStrata(
	(DMLabel)PetscToPointer((label) ),*numStrata,stratumValues);
}
PETSC_EXTERN void  dmlabeladdstratais_(DMLabel label,IS valueIS, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(valueIS);
*ierr = DMLabelAddStrataIS(
	(DMLabel)PetscToPointer((label) ),
	(IS)PetscToPointer((valueIS) ));
}
PETSC_EXTERN void  dmlabelview_(DMLabel label,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(viewer);
*ierr = DMLabelView(
	(DMLabel)PetscToPointer((label) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  dmlabelreset_(DMLabel label, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelReset(
	(DMLabel)PetscToPointer((label) ));
}
PETSC_EXTERN void  dmlabeldestroy_(DMLabel *label, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(label);
 PetscBool label_null = !*(void**) label ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelDestroy(label);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! label_null && !*(void**) label) * (void **) label = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(label);
 }
PETSC_EXTERN void  dmlabelduplicate_(DMLabel label,DMLabel *labelnew, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
PetscBool labelnew_null = !*(void**) labelnew ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(labelnew);
*ierr = DMLabelDuplicate(
	(DMLabel)PetscToPointer((label) ),labelnew);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! labelnew_null && !*(void**) labelnew) * (void **) labelnew = (void *)-2;
}
PETSC_EXTERN void  dmlabelcomputeindex_(DMLabel label, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelComputeIndex(
	(DMLabel)PetscToPointer((label) ));
}
PETSC_EXTERN void  dmlabelcreateindex_(DMLabel label,PetscInt *pStart,PetscInt *pEnd, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelCreateIndex(
	(DMLabel)PetscToPointer((label) ),*pStart,*pEnd);
}
PETSC_EXTERN void  dmlabeldestroyindex_(DMLabel label, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelDestroyIndex(
	(DMLabel)PetscToPointer((label) ));
}
PETSC_EXTERN void  dmlabelgetbounds_(DMLabel label,PetscInt *pStart,PetscInt *pEnd, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLINTEGER(pStart);
CHKFORTRANNULLINTEGER(pEnd);
*ierr = DMLabelGetBounds(
	(DMLabel)PetscToPointer((label) ),pStart,pEnd);
}
PETSC_EXTERN void  dmlabelhasvalue_(DMLabel label,PetscInt *value,PetscBool *contains, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelHasValue(
	(DMLabel)PetscToPointer((label) ),*value,contains);
}
PETSC_EXTERN void  dmlabelhaspoint_(DMLabel label,PetscInt *point,PetscBool *contains, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelHasPoint(
	(DMLabel)PetscToPointer((label) ),*point,contains);
}
PETSC_EXTERN void  dmlabelstratumhaspoint_(DMLabel label,PetscInt *value,PetscInt *point,PetscBool *contains, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelStratumHasPoint(
	(DMLabel)PetscToPointer((label) ),*value,*point,contains);
}
PETSC_EXTERN void  dmlabelgetdefaultvalue_(DMLabel label,PetscInt *defaultValue, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLINTEGER(defaultValue);
*ierr = DMLabelGetDefaultValue(
	(DMLabel)PetscToPointer((label) ),defaultValue);
}
PETSC_EXTERN void  dmlabelsetdefaultvalue_(DMLabel label,PetscInt *defaultValue, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelSetDefaultValue(
	(DMLabel)PetscToPointer((label) ),*defaultValue);
}
PETSC_EXTERN void  dmlabelgetvalue_(DMLabel label,PetscInt *point,PetscInt *value, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLINTEGER(value);
*ierr = DMLabelGetValue(
	(DMLabel)PetscToPointer((label) ),*point,value);
}
PETSC_EXTERN void  dmlabelsetvalue_(DMLabel label,PetscInt *point,PetscInt *value, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelSetValue(
	(DMLabel)PetscToPointer((label) ),*point,*value);
}
PETSC_EXTERN void  dmlabelclearvalue_(DMLabel label,PetscInt *point,PetscInt *value, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelClearValue(
	(DMLabel)PetscToPointer((label) ),*point,*value);
}
PETSC_EXTERN void  dmlabelinsertis_(DMLabel label,IS is,PetscInt *value, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(is);
*ierr = DMLabelInsertIS(
	(DMLabel)PetscToPointer((label) ),
	(IS)PetscToPointer((is) ),*value);
}
PETSC_EXTERN void  dmlabelgetnumvalues_(DMLabel label,PetscInt *numValues, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLINTEGER(numValues);
*ierr = DMLabelGetNumValues(
	(DMLabel)PetscToPointer((label) ),numValues);
}
PETSC_EXTERN void  dmlabelgetvalueis_(DMLabel label,IS *values, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
PetscBool values_null = !*(void**) values ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(values);
*ierr = DMLabelGetValueIS(
	(DMLabel)PetscToPointer((label) ),values);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! values_null && !*(void**) values) * (void **) values = (void *)-2;
}
PETSC_EXTERN void  dmlabelgetvaluebounds_(DMLabel label,PetscInt *minValue,PetscInt *maxValue, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLINTEGER(minValue);
CHKFORTRANNULLINTEGER(maxValue);
*ierr = DMLabelGetValueBounds(
	(DMLabel)PetscToPointer((label) ),minValue,maxValue);
}
PETSC_EXTERN void  dmlabelgetnonemptystratumvaluesis_(DMLabel label,IS *values, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
PetscBool values_null = !*(void**) values ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(values);
*ierr = DMLabelGetNonEmptyStratumValuesIS(
	(DMLabel)PetscToPointer((label) ),values);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! values_null && !*(void**) values) * (void **) values = (void *)-2;
}
PETSC_EXTERN void  dmlabelgetvalueindex_(DMLabel label,PetscInt *value,PetscInt *index, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLINTEGER(index);
*ierr = DMLabelGetValueIndex(
	(DMLabel)PetscToPointer((label) ),*value,index);
}
PETSC_EXTERN void  dmlabelhasstratum_(DMLabel label,PetscInt *value,PetscBool *exists, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelHasStratum(
	(DMLabel)PetscToPointer((label) ),*value,exists);
}
PETSC_EXTERN void  dmlabelgetstratumsize_(DMLabel label,PetscInt *value,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLINTEGER(size);
*ierr = DMLabelGetStratumSize(
	(DMLabel)PetscToPointer((label) ),*value,size);
}
PETSC_EXTERN void  dmlabelgetstratumbounds_(DMLabel label,PetscInt *value,PetscInt *start,PetscInt *end, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLINTEGER(start);
CHKFORTRANNULLINTEGER(end);
*ierr = DMLabelGetStratumBounds(
	(DMLabel)PetscToPointer((label) ),*value,start,end);
}
PETSC_EXTERN void  dmlabelgetstratumis_(DMLabel label,PetscInt *value,IS *points, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
PetscBool points_null = !*(void**) points ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(points);
*ierr = DMLabelGetStratumIS(
	(DMLabel)PetscToPointer((label) ),*value,points);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! points_null && !*(void**) points) * (void **) points = (void *)-2;
}
PETSC_EXTERN void  dmlabelsetstratumis_(DMLabel label,PetscInt *value,IS is, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(is);
*ierr = DMLabelSetStratumIS(
	(DMLabel)PetscToPointer((label) ),*value,
	(IS)PetscToPointer((is) ));
}
PETSC_EXTERN void  dmlabelclearstratum_(DMLabel label,PetscInt *value, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelClearStratum(
	(DMLabel)PetscToPointer((label) ),*value);
}
PETSC_EXTERN void  dmlabelsetstratumbounds_(DMLabel label,PetscInt *value,PetscInt *pStart,PetscInt *pEnd, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelSetStratumBounds(
	(DMLabel)PetscToPointer((label) ),*value,*pStart,*pEnd);
}
PETSC_EXTERN void  dmlabelgetstratumpointindex_(DMLabel label,PetscInt *value,PetscInt *p,PetscInt *index, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLINTEGER(index);
*ierr = DMLabelGetStratumPointIndex(
	(DMLabel)PetscToPointer((label) ),*value,*p,index);
}
PETSC_EXTERN void  dmlabelfilter_(DMLabel label,PetscInt *start,PetscInt *end, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelFilter(
	(DMLabel)PetscToPointer((label) ),*start,*end);
}
PETSC_EXTERN void  dmlabelpermute_(DMLabel label,IS permutation,DMLabel *labelNew, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(permutation);
PetscBool labelNew_null = !*(void**) labelNew ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(labelNew);
*ierr = DMLabelPermute(
	(DMLabel)PetscToPointer((label) ),
	(IS)PetscToPointer((permutation) ),labelNew);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! labelNew_null && !*(void**) labelNew) * (void **) labelNew = (void *)-2;
}
PETSC_EXTERN void  dmlabeldistribute_(DMLabel label,PetscSF sf,DMLabel *labelNew, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(sf);
PetscBool labelNew_null = !*(void**) labelNew ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(labelNew);
*ierr = DMLabelDistribute(
	(DMLabel)PetscToPointer((label) ),
	(PetscSF)PetscToPointer((sf) ),labelNew);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! labelNew_null && !*(void**) labelNew) * (void **) labelNew = (void *)-2;
}
PETSC_EXTERN void  dmlabelgather_(DMLabel label,PetscSF sf,DMLabel *labelNew, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(sf);
PetscBool labelNew_null = !*(void**) labelNew ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(labelNew);
*ierr = DMLabelGather(
	(DMLabel)PetscToPointer((label) ),
	(PetscSF)PetscToPointer((sf) ),labelNew);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! labelNew_null && !*(void**) labelNew) * (void **) labelNew = (void *)-2;
}
PETSC_EXTERN void  dmlabelpropagatebegin_(DMLabel label,PetscSF sf, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(sf);
*ierr = DMLabelPropagateBegin(
	(DMLabel)PetscToPointer((label) ),
	(PetscSF)PetscToPointer((sf) ));
}
PETSC_EXTERN void  dmlabelpropagateend_(DMLabel label,PetscSF pointSF, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(pointSF);
*ierr = DMLabelPropagateEnd(
	(DMLabel)PetscToPointer((label) ),
	(PetscSF)PetscToPointer((pointSF) ));
}
PETSC_EXTERN void  dmlabelconverttosection_(DMLabel label,PetscSection *section,IS *is, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
PetscBool section_null = !*(void**) section ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(section);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
*ierr = DMLabelConvertToSection(
	(DMLabel)PetscToPointer((label) ),section,is);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! section_null && !*(void**) section) * (void **) section = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
}
PETSC_EXTERN void  dmlabelsettype_(DMLabel label,char *method, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(label);
/* insert Fortran-to-C conversion for method */
  FIXCHAR(method,cl0,_cltmp0);
*ierr = DMLabelSetType(
	(DMLabel)PetscToPointer((label) ),_cltmp0);
  FREECHAR(method,_cltmp0);
}
PETSC_EXTERN void  dmlabelgettype_(DMLabel label,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(label);
*ierr = DMLabelGetType(
	(DMLabel)PetscToPointer((label) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  petscsectioncreateglobalsectionlabel_(PetscSection s,PetscSF sf,PetscBool *includeConstraints,DMLabel label,PetscInt *labelValue,PetscSection *gsection, int *ierr)
{
CHKFORTRANNULLOBJECT(s);
CHKFORTRANNULLOBJECT(sf);
CHKFORTRANNULLOBJECT(label);
PetscBool gsection_null = !*(void**) gsection ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(gsection);
*ierr = PetscSectionCreateGlobalSectionLabel(
	(PetscSection)PetscToPointer((s) ),
	(PetscSF)PetscToPointer((sf) ),*includeConstraints,
	(DMLabel)PetscToPointer((label) ),*labelValue,gsection);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! gsection_null && !*(void**) gsection) * (void **) gsection = (void *)-2;
}
PETSC_EXTERN void  petscsectionsymlabelsetlabel_(PetscSectionSym sym,DMLabel label, int *ierr)
{
CHKFORTRANNULLOBJECT(sym);
CHKFORTRANNULLOBJECT(label);
*ierr = PetscSectionSymLabelSetLabel(
	(PetscSectionSym)PetscToPointer((sym) ),
	(DMLabel)PetscToPointer((label) ));
}
PETSC_EXTERN void  petscsectionsymcreatelabel_(MPI_Fint * comm,DMLabel label,PetscSectionSym *sym, int *ierr)
{
CHKFORTRANNULLOBJECT(label);
PetscBool sym_null = !*(void**) sym ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sym);
*ierr = PetscSectionSymCreateLabel(
	MPI_Comm_f2c(*(comm)),
	(DMLabel)PetscToPointer((label) ),sym);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sym_null && !*(void**) sym) * (void **) sym = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
